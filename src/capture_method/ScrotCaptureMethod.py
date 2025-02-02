import sys

if sys.platform != "linux":
    raise OSError

import cv2
import numpy as np
import pyscreeze
from pywinctl import getWindowsWithTitle
from typing_extensions import override
from Xlib.display import Display
from Xlib.error import BadWindow

from capture_method.CaptureMethodBase import CaptureMethodBase
from utils import is_valid_image


class ScrotCaptureMethod(CaptureMethodBase):
    name = "Scrot"
    short_description = "very slow, may leave files"
    description = (
        "\nUses Scrot (SCReenshOT) to take screenshots. "
        + "\nLeaves behind a screenshot file if interrupted. "
    )

    @override
    def get_frame(self):
        if not self.check_selected_region_exists():
            return None
        xdisplay = Display()
        root = xdisplay.screen().root
        try:
            data = root.translate_coords(self._autosplit_ref.hwnd, 0, 0)._data  # noqa: SLF001
        except BadWindow:
            return None
        offset_x = data["x"]
        offset_y = data["y"]
        selection = self._autosplit_ref.settings_dict["capture_region"]
        image = pyscreeze.screenshot(
            None,
            (
                selection["x"] + offset_x,
                selection["y"] + offset_y,
                selection["width"],
                selection["height"],
            ),
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
