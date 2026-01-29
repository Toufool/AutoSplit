import sys

if sys.platform != "linux":
    raise OSError

from typing import override

import cv2
import numpy as np
from PIL import ImageGrab
from pywinctl import getWindowsWithTitle
from Xlib.display import Display
from Xlib.error import BadWindow

from capture_method.CaptureMethodBase import CaptureMethodBase
from utils import is_valid_image


class XcbCaptureMethod(CaptureMethodBase):
    name = "X11 XCB"
    short_description = "fast, requires XCB"
    description = "\nUses the XCB library to take screenshots of the X11 server."

    _xdisplay: str | None = ""  # ":0"

    @override
    def get_frame(self):
        if not self.check_selected_region_exists():
            return None

        root = Display().screen().root
        try:
            window_coords = root.translate_coords(self._autosplit_ref.hwnd, 0, 0)._data  # noqa: SLF001
        except BadWindow:
            return None
        # image = window.get_image(
        #     selection["x"],
        #     selection["y"],
        #     selection["width"],
        #     selection["height"],
        #     1,
        #     0,
        # )

        selection = self._autosplit_ref.settings_dict["capture_region"]
        x = selection["x"] + window_coords["x"]
        y = selection["y"] + window_coords["y"]
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
        windows = getWindowsWithTitle(captured_window_title)
        if len(windows) == 0:
            return False
        self._autosplit_ref.hwnd = windows[0].getHandle()
        return self.check_selected_region_exists()
