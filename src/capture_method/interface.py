from __future__ import annotations

import cv2

from utils import find_autosplit_main_window, is_valid_hwnd


# pylint: disable=no-self-use,unnecessary-dunder-call
class CaptureMethodBase():

    def __init__(self):
        self.autosplit = find_autosplit_main_window()

    def close(self):
        # Some capture methods don't need to cleanup and release any resource
        pass

    def reinitialize(self):
        self.close()
        self.__init__()

    def get_frame(self) -> tuple[cv2.Mat | None, bool]:
        """
        Captures an image of the region for a window matching the given
        parameters of the bounding box

        @return: The image of the region in the window in BGRA format
        """
        return None, False

    def recover_window(self, captured_window_title: str) -> bool:
        return False

    def check_selected_region_exists(self) -> bool:
        return is_valid_hwnd(self.autosplit.hwnd)
# pylint: enable=no-self-use,unnecessary-dunder-call
