from typing import TYPE_CHECKING

from cv2.typing import MatLike

from utils import is_valid_hwnd

if TYPE_CHECKING:
    from AutoSplit import AutoSplit


class CaptureMethodBase:
    name = "None"
    short_description = ""
    description = ""

    _autosplit_ref: "AutoSplit"

    def __init__(self, autosplit: "AutoSplit"):
        # Some capture methods don't need an initialization process
        self._autosplit_ref = autosplit

    def reinitialize(self):
        self.close()
        self.__init__(self._autosplit_ref)  # type: ignore[misc]

    def close(self):
        # Some capture methods don't need an initialization process
        pass

    def get_frame(self) -> tuple[MatLike | None, bool]:  # noqa: PLR6301
        """
        Captures an image of the region for a window matching the given
        parameters of the bounding box.

        @return: The image of the region in the window in BGRA format
        """
        return None, False

    def recover_window(self, captured_window_title: str) -> bool:  # noqa: PLR6301
        return False

    def check_selected_region_exists(self) -> bool:
        return is_valid_hwnd(self._autosplit_ref.hwnd)
