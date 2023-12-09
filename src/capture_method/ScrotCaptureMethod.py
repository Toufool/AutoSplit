import sys

if sys.platform != "linux":
    raise OSError

import cv2
import numpy as np
import pyscreeze
from typing_extensions import override
from Xlib.display import Display

from capture_method.CaptureMethodBase import ThreadedLoopCaptureMethod
from utils import is_valid_image


class ScrotCaptureMethod(ThreadedLoopCaptureMethod):
    name = "Scrot"
    short_description = "very slow, may leave files"
    description = (
        "\nUses Scrot (SCReenshOT) to take screenshots. "
        + "\nLeaves behind a screenshot file if interrupted. "
    )

    @override
    def _read_action(self):
        if not self.check_selected_region_exists():
            return None
        xdisplay = Display()
        root = xdisplay.screen().root
        data = root.translate_coords(self._autosplit_ref.hwnd, 0, 0)._data  # noqa: SLF001
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
        return np.array(image)

    @override
    def get_frame(self):
        image = super().get_frame()
        if not is_valid_image(image):
            return None
        return cv2.cvtColor(image, cv2.COLOR_RGB2BGRA)
