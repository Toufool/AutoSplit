import sys

if sys.platform != "win32":
    raise OSError
import asyncio
from typing import TYPE_CHECKING, cast

import numpy as np
import win32gui
from cv2.typing import MatLike
from typing_extensions import override
from winsdk.windows.graphics import SizeInt32
from winsdk.windows.graphics.capture import Direct3D11CaptureFramePool, GraphicsCaptureSession
from winsdk.windows.graphics.capture.interop import create_for_window
from winsdk.windows.graphics.directx import DirectXPixelFormat
from winsdk.windows.graphics.directx.direct3d11 import IDirect3DSurface
from winsdk.windows.graphics.imaging import BitmapBufferAccessMode, SoftwareBitmap

from capture_method.CaptureMethodBase import ThreadedLoopCaptureMethod
from utils import (
    BGRA_CHANNEL_COUNT,
    WGC_MIN_BUILD,
    WINDOWS_BUILD_NUMBER,
    get_direct3d_device,
    is_valid_hwnd,
)

if TYPE_CHECKING:
    from AutoSplit import AutoSplit

WGC_NO_BORDER_MIN_BUILD = 20348

WGC_QTIMER_LIMIT = 30


async def convert_d3d_surface_to_software_bitmap(surface: IDirect3DSurface | None):
    return await SoftwareBitmap.create_copy_from_surface_async(surface)


class WindowsGraphicsCaptureMethod(ThreadedLoopCaptureMethod):
    name = "Windows Graphics Capture"
    short_description = "fast, most compatible, capped at 60fps"
    description = (
        f"\nOnly available in Windows 10.0.{WGC_MIN_BUILD} and up. "
        + "\nAllows recording UWP apps, Hardware Accelerated and Exclusive Fullscreen windows. "
        + "\nAdds a yellow border on Windows 10 (not on Windows 11)."
        + "\nCaps at around 60 FPS. "
    )

    size: SizeInt32
    frame_pool: Direct3D11CaptureFramePool | None = None
    session: GraphicsCaptureSession | None = None
    """This is stored to prevent session from being garbage collected"""

    def __init__(self, autosplit: "AutoSplit"):
        super().__init__(autosplit)
        if not is_valid_hwnd(autosplit.hwnd):
            return

        item = create_for_window(autosplit.hwnd)
        frame_pool = Direct3D11CaptureFramePool.create_free_threaded(
            get_direct3d_device(),
            DirectXPixelFormat.B8_G8_R8_A8_UINT_NORMALIZED,
            1,
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
    def set_fps_limit(self, fps: int):
        """
        There's an issue in the interaction between QTimer and WGC API where setting the interval to
        even 1 ms causes twice as many "called `try_get_next_frame` too fast".
        So for FPS target above 30, we unlock interval speed.
        """
        super().set_fps_limit(fps if fps <= WGC_QTIMER_LIMIT else 0)

    @override
    def _read_action(self) -> MatLike | None:
        selection = self._autosplit_ref.settings_dict["capture_region"]
        # Only needed for the type-checker
        if not self.frame_pool:
            return None

        try:
            frame = self.frame_pool.try_get_next_frame()
        # Frame pool is closed
        except OSError:
            return None

        # We were too fast and the next frame wasn't ready yet
        if not frame:
            return self.last_captured_image

        try:
            software_bitmap = asyncio.run(convert_d3d_surface_to_software_bitmap(frame.surface))
        except SystemError as exception:
            # HACK: can happen when closing the GraphicsCapturePicker
            if str(exception).endswith("returned a result with an error set"):
                return self.last_captured_image
            raise

        if not software_bitmap:
            # HACK: Can happen when starting the region selector
            # TODO: Validate if this is still true
            return self.last_captured_image
            # raise ValueError("Unable to convert IDirect3DSurface to SoftwareBitmap.")
        bitmap_buffer = software_bitmap.lock_buffer(BitmapBufferAccessMode.READ_WRITE)
        if not bitmap_buffer:
            raise ValueError("Unable to obtain the BitmapBuffer from SoftwareBitmap.")
        reference = bitmap_buffer.create_reference()
        image = np.frombuffer(cast(bytes, reference), dtype=np.uint8)
        image.shape = (self.size.height, self.size.width, BGRA_CHANNEL_COUNT)
        return image[
            selection["y"] : selection["y"] + selection["height"],
            selection["x"] : selection["x"] + selection["width"],
        ]

    @override
    def recover_window(self, captured_window_title: str):
        hwnd = win32gui.FindWindow(None, captured_window_title)
        if not is_valid_hwnd(hwnd):
            return False

        # Because of async image obtention and capture initialization, AutoSplit
        # could ask for an image too soon after having called recover_window() last iteration.
        # WGC *would* have returned an image, but it's asked to reinitialize over again.
        if self._autosplit_ref.hwnd == hwnd and self.check_selected_region_exists():
            return True

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
            and self.session,
        )
