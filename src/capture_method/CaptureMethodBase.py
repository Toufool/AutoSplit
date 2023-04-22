from __future__ import annotations

from typing import TYPE_CHECKING

import cv2

from utils import is_valid_hwnd

if TYPE_CHECKING:
    from AutoSplit import AutoSplit


class CaptureMethodBase():
    def __init__(self, autosplit: AutoSplit | None = None):
        # Some capture methods don't need an initialization process
        pass

    def reinitialize(self, autosplit: AutoSplit):
        self.close(autosplit)
        self.__init__(autosplit)  # pylint: disable=unnecessary-dunder-call

    def close(self, autosplit: AutoSplit):
        # Some capture methods don't need an initialization process
        pass

    def get_frame(self, autosplit: AutoSplit) -> tuple[cv2.Mat | None, bool]:
        """
        Captures an image of the region for a window matching the given
        parameters of the bounding box

        @return: The image of the region in the window in BGRA format
        """
        return None, False

    def recover_window(self, captured_window_title: str, autosplit: AutoSplit) -> bool:
        return False

    def check_selected_region_exists(self, autosplit: AutoSplit) -> bool:
        return is_valid_hwnd(autosplit.hwnd)
