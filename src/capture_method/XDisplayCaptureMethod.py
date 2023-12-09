import sys

if sys.platform != "linux":
    raise OSError

import cv2
import numpy as np
from PIL import ImageGrab
from typing_extensions import override
from Xlib.display import Display

from capture_method.CaptureMethodBase import ThreadedLoopCaptureMethod
from utils import is_valid_image


class XDisplayCaptureMethod(ThreadedLoopCaptureMethod):
    name = "XDisplay"
    short_description = "fast, requires xcb"
    description = "\nUses XCB to take screenshots of the display"

    _xdisplay: str | None = ""  # ":0"

    @override
    def _read_action(self):
        if not self.check_selected_region_exists():
            return None
        xdisplay = Display()
        root = xdisplay.screen().root
        data = root.translate_coords(self._autosplit_ref.hwnd, 0, 0)._data  # noqa: SLF001
        offset_x = data["x"]
        offset_y = data["y"]
        # image = window.get_image(selection["x"], selection["y"], selection["width"], selection["height"], 1, 0)

        selection = self._autosplit_ref.settings_dict["capture_region"]
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
        image = np.array(image)
        if not is_valid_image(image):
            return None
        return cv2.cvtColor(image, cv2.COLOR_RGB2BGRA)

    @override
    def recover_window(self, captured_window_title: str):
        xdisplay = Display()
        root = xdisplay.screen().root
        children = root.query_tree().children
        for window in children:
            wm_class = window.get_wm_class()
            if wm_class and wm_class[1] == captured_window_title:
                self._autosplit_ref.hwnd = window.id
                return self.check_selected_region_exists()
        return False
