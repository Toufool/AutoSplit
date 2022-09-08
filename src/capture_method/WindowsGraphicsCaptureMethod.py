from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, cast

import cv2
import numpy as np
from win32 import win32gui
from winsdk.windows.graphics import SizeInt32
from winsdk.windows.graphics.capture import Direct3D11CaptureFramePool, GraphicsCaptureSession
from winsdk.windows.graphics.capture.interop import create_for_window
from winsdk.windows.graphics.directx import DirectXPixelFormat
from winsdk.windows.graphics.imaging import BitmapBufferAccessMode, SoftwareBitmap
from winsdk.windows.media.capture import MediaCapture

from capture_method.CaptureMethodBase import CaptureMethodBase
from utils import WINDOWS_BUILD_NUMBER, is_valid_hwnd

if TYPE_CHECKING:
    from AutoSplit import AutoSplit

WGC_NO_BORDER_MIN_BUILD = 20348


class WindowsGraphicsCaptureMethod(CaptureMethodBase):
    size: SizeInt32
    frame_pool: Direct3D11CaptureFramePool | None = None
    session: GraphicsCaptureSession | None = None
    """This is stored to prevent session from being garbage collected"""
    last_captured_frame: cv2.Mat | None = None

    def __init__(self, autosplit: AutoSplit):
        super().__init__(autosplit)
        if not is_valid_hwnd(autosplit.hwnd):
            return
        # Note: Must create in the same thread (can't use a global) otherwise when ran from LiveSplit it will raise:
        # OSError: The application called an interface that was marshalled for a different thread
        media_capture = MediaCapture()
        item = create_for_window(autosplit.hwnd)

        async def coroutine():
            await (media_capture.initialize_async() or asyncio.sleep(0))
        asyncio.run(coroutine())

        if not media_capture.media_capture_settings:
            raise OSError("Unable to initialize a Direct3D Device.")
        frame_pool = Direct3D11CaptureFramePool.create_free_threaded(
            media_capture.media_capture_settings.direct3_d11_device,
            DirectXPixelFormat.B8_G8_R8_A8_UINT_NORMALIZED,
            1,
            item.size)
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

    def close(self, autosplit: AutoSplit):
        if self.frame_pool:
            self.frame_pool.close()
            self.frame_pool = None
        if self.session:
            try:
                self.session.close()
            except OSError:
                # OSError: The application called an interface that was marshalled for a different thread
                # This still seems to close the session and prevent the following hard crash in LiveSplit
                # pylint: disable=line-too-long
                # "AutoSplit.exe	<process started at 00:05:37.020 has terminated with 0xc0000409 (EXCEPTION_STACK_BUFFER_OVERRUN)>"  # noqa E501
                pass
            self.session = None

    def get_frame(self, autosplit: AutoSplit) -> tuple[cv2.Mat | None, bool]:
        selection = autosplit.settings_dict["capture_region"]
        # We still need to check the hwnd because WGC will return a blank black image
        if not (self.check_selected_region_exists(autosplit)
                # Only needed for the type-checker
                and self.frame_pool):
            return None, False

        try:
            frame = self.frame_pool.try_get_next_frame()
        # Frame pool is closed
        except OSError:
            return None, False

        # We were too fast and the next frame wasn't ready yet
        if not frame:
            return self.last_captured_frame, True

        async def coroutine():
            return await (SoftwareBitmap.create_copy_from_surface_async(frame.surface) or asyncio.sleep(0, None))
        try:
            software_bitmap = asyncio.run(coroutine())
        except SystemError as exception:
            # HACK: can happen when closing the GraphicsCapturePicker
            if str(exception).endswith("returned a result with an error set"):
                return self.last_captured_frame, True
            raise

        if not software_bitmap:
            # HACK: Can happen when starting the region selector
            return self.last_captured_frame, True
            # raise ValueError("Unable to convert Direct3D11CaptureFrame to SoftwareBitmap.")
        bitmap_buffer = software_bitmap.lock_buffer(BitmapBufferAccessMode.READ_WRITE)
        if not bitmap_buffer:
            raise ValueError("Unable to obtain the BitmapBuffer from SoftwareBitmap.")
        reference = bitmap_buffer.create_reference()
        image = np.frombuffer(cast(bytes, reference), dtype=np.uint8)
        image.shape = (self.size.height, self.size.width, 4)
        image = image[
            selection["y"]:selection["y"] + selection["height"],
            selection["x"]:selection["x"] + selection["width"],
        ]
        self.last_captured_frame = image
        return image, False

    def recover_window(self, captured_window_title: str, autosplit: AutoSplit):
        hwnd = win32gui.FindWindow(None, captured_window_title)
        if not is_valid_hwnd(hwnd):
            return False
        autosplit.hwnd = hwnd
        self.close(autosplit)
        try:
            self.__init__(autosplit)  # pylint: disable=unnecessary-dunder-call  # type: ignore[misc]
        # Unrecordable hwnd found as the game is crashing
        except OSError as exception:
            if str(exception).endswith("The parameter is incorrect"):
                return False
            raise
        return self.check_selected_region_exists(autosplit)

    def check_selected_region_exists(self, autosplit: AutoSplit):
        return bool(
            is_valid_hwnd(autosplit.hwnd)
            and self.frame_pool
            and self.session)
