from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import cv2

if TYPE_CHECKING:
    from AutoSplit import AutoSplit


class CaptureMethodInterface():
    def __init__(self, autosplit: Optional[AutoSplit] = None):
        pass

    def reinitialize(self, autosplit: AutoSplit):
        self.close(autosplit)
        self.__init__(autosplit)  # pylint: disable=unnecessary-dunder-call

    def close(self, autosplit: AutoSplit):
        pass

    def get_frame(self, autosplit: AutoSplit) -> tuple[Optional[cv2.Mat], bool]:
        """
        Captures an image of the region for a window matching the given
        parameters of the bounding box

        @return: The image of the region in the window in BGRA format
        """
        raise NotImplementedError()

    def recover_window(self, captured_window_title: str, autosplit: AutoSplit) -> bool:
        raise NotImplementedError()

    def check_selected_region_exists(self, autosplit: AutoSplit) -> bool:
        raise NotImplementedError()