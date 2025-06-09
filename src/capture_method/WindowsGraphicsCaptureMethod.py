import sys

if sys.platform != "win32":
    raise OSError
import asyncio
from typing import TYPE_CHECKING, cast, override

import numpy as np
import win32gui
from cv2.typing import MatLike
from winrt.windows.graphics import SizeInt32
from winrt.windows.graphics.capture import Direct3D11CaptureFramePool, GraphicsCaptureSession
from winrt.windows.graphics.capture.interop import create_for_window
from winrt.windows.graphics.directx import DirectXPixelFormat
from winrt.windows.graphics.directx.direct3d11 import IDirect3DSurface
from winrt.windows.graphics.directx.direct3d11.interop import (
    create_direct3d11_device_from_dxgi_device,
)
from winrt.windows.graphics.imaging import BitmapBufferAccessMode, SoftwareBitmap

from capture_method.CaptureMethodBase import CaptureMethodBase
from d3d11 import D3D11_CREATE_DEVICE_FLAG, D3D_DRIVER_TYPE, D3D11CreateDevice
from utils import BGRA_CHANNEL_COUNT, WGC_MIN_BUILD, WINDOWS_BUILD_NUMBER, is_valid_hwnd

if TYPE_CHECKING:
    from AutoSplit import AutoSplit

WGC_NO_BORDER_MIN_BUILD = 20348


async def convert_d3d_surface_to_software_bitmap(surface: IDirect3DSurface):
    return await SoftwareBitmap.create_copy_from_surface_async(surface)


class WindowsGraphicsCaptureMethod(CaptureMethodBase):
    name = "Windows Graphics Capture"
    short_description = "fast, most compatible, capped at 60fps"
    description = f"""
Only available in Windows 10.0.{WGC_MIN_BUILD} and up.
Allows recording UWP apps, Hardware Accelerated and Exclusive Fullscreen windows.
Adds a yellow border on Windows 10 (not on Windows 11).
Caps at around 60 FPS."""

    size: "SizeInt32"
    frame_pool: Direct3D11CaptureFramePool | None = None
    session: GraphicsCaptureSession | None = None
    """This is stored to prevent session from being garbage collected"""
    last_converted_frame: MatLike | None = None

    def __init__(self, autosplit: "AutoSplit"):
        super().__init__(autosplit)
        if not is_valid_hwnd(autosplit.hwnd):
            return

        dxgi, *_ = D3D11CreateDevice(
            DriverType=D3D_DRIVER_TYPE.HARDWARE,
            Flags=D3D11_CREATE_DEVICE_FLAG.BGRA_SUPPORT,
        )
        direct3d_device = create_direct3d11_device_from_dxgi_device(dxgi.value)
        item = create_for_window(autosplit.hwnd)
        frame_pool = Direct3D11CaptureFramePool.create_free_threaded(
            direct3d_device,
            DirectXPixelFormat.B8_G8_R8_A8_UINT_NORMALIZED,
            1,  # number_of_buffers
            item.size,
        )
        if not frame_pool:
            raise OSError("Unable to create a frame pool for a capture session.")
        session = frame_pool.create_capture_session(item)
        if not session:
            raise OSError("Unable to create a capture session.")
        session.is_cursor_capture_enabled = False
        if WINDOWS_BUILD_NUMBER >= WGC_NO_BORDER_MIN_BUILD:
            session.is_border_required = False
        session.start_capture()

        self.session = session
        self.size = item.size
        self.frame_pool = frame_pool

    @override
    def close(self):
        super().close()
        if self.frame_pool:
            self.frame_pool.close()
            self.frame_pool = None
        if self.session:
            try:
                self.session.close()
            except OSError:
                # OSError: The application called an interface that was marshalled for a different thread # noqa: E501
                # This still seems to close the session and prevent the following hard crash in LiveSplit # noqa: E501
                # "AutoSplit.exe	<process started at 00:05:37.020 has terminated with 0xc0000409 (EXCEPTION_STACK_BUFFER_OVERRUN)>" # noqa: E501
                pass
            self.session = None

    @override
    def get_frame(self) -> MatLike | None:
        selection = self._autosplit_ref.settings_dict["capture_region"]
        # We still need to check the hwnd because WGC will return a blank black image
        if not (
            self.check_selected_region_exists()
            # Only needed for the type-checker
            and self.frame_pool
        ):
            return None

        try:
            frame = self.frame_pool.try_get_next_frame()
        # Frame pool is closed
        except OSError:
            return None

        # We were too fast and the next frame wasn't ready yet
        # TODO: Consider "add_frame_arrive" instead !
        # https://github.com/pywinrt/pywinrt/blob/5bf1ac5ff4a77cf343e11d7c841c368fa9235d81/samples/screen_capture/__main__.py#L67-L78
        if not frame:
            return self.last_converted_frame

        try:
            software_bitmap = asyncio.run(convert_d3d_surface_to_software_bitmap(frame.surface))
        except SystemError as exception:
            # HACK: can happen when closing the GraphicsCapturePicker
            if str(exception).endswith("returned a result with an error set"):
                return self.last_converted_frame
            raise

        if not software_bitmap:
            # HACK: Can happen when starting the region selector
            # TODO: Validate if this is still true
            return self.last_converted_frame
            # raise ValueError("Unable to convert Direct3D11CaptureFrame to SoftwareBitmap.")
        bitmap_buffer = software_bitmap.lock_buffer(BitmapBufferAccessMode.READ_WRITE)
        if not bitmap_buffer:
            raise ValueError("Unable to obtain the BitmapBuffer from SoftwareBitmap.")
        reference = bitmap_buffer.create_reference()
        image = np.frombuffer(cast(bytes, reference), dtype=np.uint8)
        image.shape = (self.size.height, self.size.width, BGRA_CHANNEL_COUNT)
        image = image[
            selection["y"] : selection["y"] + selection["height"],
            selection["x"] : selection["x"] + selection["width"],
        ]
        self.last_converted_frame = image
        return image

    @override
    def recover_window(self, captured_window_title: str):
        hwnd = win32gui.FindWindow(None, captured_window_title)
        if not is_valid_hwnd(hwnd):
            return False
        self._autosplit_ref.hwnd = hwnd
        try:
            self.reinitialize()
        # Unrecordable hwnd found as the game is crashing
        except OSError as exception:
            if str(exception).endswith("The parameter is incorrect"):
                return False
            raise
        return self.check_selected_region_exists()

    @override
    def check_selected_region_exists(self):
        return bool(
            is_valid_hwnd(self._autosplit_ref.hwnd)  # fmt: skip
            and self.frame_pool
            and self.session
        )
