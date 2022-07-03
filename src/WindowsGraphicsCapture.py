import asyncio
from dataclasses import dataclass
from typing import Optional

import cv2
from winsdk.windows.graphics import SizeInt32
from winsdk.windows.graphics.capture import Direct3D11CaptureFramePool, GraphicsCaptureItem, GraphicsCaptureSession
from winsdk.windows.graphics.directx import DirectXPixelFormat
from winsdk.windows.media.capture import MediaCapture

from utils import WINDOWS_BUILD_NUMBER

WGC_NO_BORDER_MIN_BUILD = 20348


@dataclass
class WindowsGraphicsCapture:
    size: SizeInt32
    frame_pool: Direct3D11CaptureFramePool
    # Prevent session from being garbage collected
    session: GraphicsCaptureSession
    last_captured_frame: Optional[cv2.Mat]

    def close(self):
        self.frame_pool.close()
        try:
            self.session.close()
        except OSError:
            # OSError: The application called an interface that was marshalled for a different thread
            # This still seems to close the session and prevent the following hard crash in LiveSplit
            # pylint: disable=line-too-long
            # "AutoSplit.exe	<process started at 00:05:37.020 has terminated with 0xc0000409 (EXCEPTION_STACK_BUFFER_OVERRUN)>"  # noqa: E501
            pass


def create_windows_graphics_capture(item: GraphicsCaptureItem):
    # Note: Must create in the same thread (can't use a global) otherwise when ran from LiveSplit it will raise:
    # OSError: The application called an interface that was marshalled for a different thread
    media_capture = MediaCapture()

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
    return WindowsGraphicsCapture(item.size, frame_pool, session, None)
