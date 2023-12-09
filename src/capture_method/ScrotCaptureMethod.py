from __future__ import annotations

import sys

if sys.platform != "linux":
    raise OSError

from typing import TYPE_CHECKING

import cv2
import numpy as np
import pyscreeze
from Xlib.display import Display

from capture_method.CaptureMethodBase import ThreadedCaptureMethod
from utils import is_valid_image

if TYPE_CHECKING:
    from AutoSplit import AutoSplit


class ScrotCaptureMethod(ThreadedCaptureMethod):
    name = "Scrot"
    short_description = "very slow, may leave files"
    description = (
        "\nUses Scrot (SCReenshOT) to take screenshots. "
        + "\nLeaves behind a screenshot file if interrupted. "
    )

    def _read_action(self, autosplit: AutoSplit):
        if not self.check_selected_region_exists(autosplit):
            return None, False
        xdisplay = Display()
        root = xdisplay.screen().root
        # pylint: disable=protected-access
        data = root.translate_coords(autosplit.hwnd, 0, 0)._data  # noqa: SLF001
        offset_x = data["x"]
        offset_y = data["y"]
        selection = autosplit.settings_dict["capture_region"]
        image = pyscreeze.screenshot(
            None,
            (
                selection["x"] + offset_x,
                selection["y"] + offset_y,
                selection["width"],
                selection["height"],
            ),
        )
        return np.array(image), False

    def get_frame(self, autosplit: AutoSplit):
        image, is_old_image = super().get_frame(autosplit)
        if not is_valid_image(image):
            return None, is_old_image
        return cv2.cvtColor(image, cv2.COLOR_RGB2BGRA), is_old_image
