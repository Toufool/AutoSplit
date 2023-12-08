from __future__ import annotations

import sys

if sys.platform != "linux":
    raise OSError

from typing import TYPE_CHECKING

import cv2
import numpy as np
from PIL import ImageGrab
from Xlib.display import Display

from capture_method.CaptureMethodBase import ThreadedCaptureMethod
from utils import is_valid_image

if TYPE_CHECKING:
    from AutoSplit import AutoSplit


class XDisplayCaptureMethod(ThreadedCaptureMethod):
    name = "XDisplay"
    short_description = "fast, requires xcb"
    description = "\nUses XCB to take screenshots of the display"

    _xdisplay: str | None = ""  # ":0"

    def _read_action(self, autosplit: AutoSplit):
        if not self.check_selected_region_exists(autosplit):
            return None, False
        xdisplay = Display()
        root = xdisplay.screen().root
        # pylint: disable=protected-access
        data = root.translate_coords(autosplit.hwnd, 0, 0)._data  # noqa: SLF001
        offset_x = data["x"]
        offset_y = data["y"]
        # image = window.get_image(selection["x"], selection["y"], selection["width"], selection["height"], 1, 0)

        selection = autosplit.settings_dict["capture_region"]
        x = selection["x"] + offset_x
        y = selection["y"] + offset_y
        image = ImageGrab.grab(
            (
                x,
                y,
                x + selection["width"],
                y + selection["height"],
            ),
            xdisplay=self._xdisplay,
        )
        return np.array(image), False

    def get_frame(self, autosplit: AutoSplit):
        image, is_old_image = super().get_frame(autosplit)
        if not is_valid_image(image):
            return None, is_old_image
        return cv2.cvtColor(image, cv2.COLOR_RGB2BGRA), is_old_image

    def recover_window(self, captured_window_title: str, autosplit: AutoSplit):
        xdisplay = Display()
        root = xdisplay.screen().root
        children = root.query_tree().children
        for window in children:
            wm_class = window.get_wm_class()
            if wm_class and wm_class[1] == captured_window_title:
                autosplit.hwnd = window.id
                return self.check_selected_region_exists(autosplit)
        return False
