import sys

if sys.platform != "linux":
    raise OSError

from typing import TYPE_CHECKING, override

import cv2
import numpy as np
from Xlib import X
from Xlib.display import Display
from Xlib.error import BadDrawable, BadMatch

from capture_method.CaptureMethodBase import CaptureMethodBase
from utils import ALPHA_CHANNEL_COUNT, get_windows_with_title, is_valid_image

if TYPE_CHECKING:
    from Xlib.protocol.request import GetImage

    from AutoSplit import AutoSplit
    from capture_method import Region

ALL_PLANES = 0xFFFFFFFF


def _image_reply_to_bgr(reply: GetImage, width: int, height: int):
    image = np.frombuffer(reply.data, dtype=np.uint8)
    # X pads 24-bit depth to 32 bits per pixel (BGRX). The 4th byte is padding, not alpha.
    # Other depths (16, 30) use different pixel layouts we don't decode, so return None.
    if image.size != width * height * ALPHA_CHANNEL_COUNT:
        return None
    image = image.reshape((height, width, ALPHA_CHANNEL_COUNT))
    if not is_valid_image(image):
        return None
    return cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)


def _clamp_to_window(selection: Region, window_width: int, window_height: int):
    """@return: The (left, top, right, bottom) edges of the selection that are inside the window."""
    return (
        max(selection["x"], 0),
        max(selection["y"], 0),
        min(selection["x"] + selection["width"], window_width),
        min(selection["y"] + selection["height"], window_height),
    )


class X11CaptureMethod(CaptureMethodBase):
    name = "X11"
    short_description = "fastest"
    description = """
Requests the window's content directly from the X11 server.
Also works with X11 apps running through XWayland on Wayland."""

    def __init__(self, autosplit: AutoSplit):
        super().__init__(autosplit)
        self._display = Display()

    @override
    def close(self):
        self._display.close()

    @override
    def get_frame(self):
        if not self.check_selected_region_exists():
            return None

        # Grab from the window's own drawable rather than the root window: compositors and
        # XWayland redirect toplevels to their own pixmap, so this works even when the window is
        # partially off-screen or covered, and under rootless XWayland where the root is blank.
        window = self._display.create_resource_object("window", self._autosplit_ref.hwnd)
        selection = self._autosplit_ref.settings_dict["capture_region"]
        try:
            geometry = window.get_geometry()
            # GetImage requires the rectangle to be inside the window, so only request the part
            # that is, and pad the rest to keep the selected size.
            left, top, right, bottom = _clamp_to_window(selection, geometry.width, geometry.height)
            if right <= left or bottom <= top:
                # Region is entirely outside the window
                return None
            reply = window.get_image(left, top, right - left, bottom - top, X.ZPixmap, ALL_PLANES)
        except BadDrawable:
            # Window was closed
            return None
        except BadMatch:
            # Window isn't viewable (unmapped or minimized).
            # Without a compositor, also when the region is (partially) outside the screen.
            return None
        image = _image_reply_to_bgr(reply, right - left, bottom - top)
        if image is None:
            return None
        return cv2.copyMakeBorder(
            image,
            top - selection["y"],
            selection["y"] + selection["height"] - bottom,
            left - selection["x"],
            selection["x"] + selection["width"] - right,
            cv2.BORDER_CONSTANT,
        )

    @override
    def recover_window(self, captured_window_title: str):
        windows = get_windows_with_title(captured_window_title)
        if len(windows) == 0:
            return False
        self._autosplit_ref.hwnd = windows[0].getHandle()
        return self.check_selected_region_exists()
