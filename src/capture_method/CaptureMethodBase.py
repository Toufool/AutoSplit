from __future__ import annotations

from threading import Event, Thread
from typing import TYPE_CHECKING

import cv2

import error_messages
from utils import is_valid_hwnd

if TYPE_CHECKING:
    from AutoSplit import AutoSplit


class CaptureMethodBase():
    name = "None"
    short_description = ""
    description = ""

    def __init__(self, autosplit: AutoSplit | None = None):
        # Some capture methods don't need an initialization process
        pass

    def reinitialize(self, autosplit: AutoSplit):
        self.close(autosplit)
        self.__init__(autosplit)

    def close(self, autosplit: AutoSplit):
        # Some capture methods don't need an initialization process
        pass

    def get_frame(self, autosplit: AutoSplit) -> tuple[cv2.Mat | None, bool]:
        """
        Captures an image of the region for a window matching the given
        parameters of the bounding box.

        @return: The image of the region in the window in BGRA format
        """
        return None, False

    def recover_window(self, captured_window_title: str, autosplit: AutoSplit) -> bool:
        return False

    def check_selected_region_exists(self, autosplit: AutoSplit) -> bool:
        return is_valid_hwnd(autosplit.hwnd)


class ThreadedCaptureMethod(CaptureMethodBase):
    _last_captured_frame: cv2.Mat | None = None
    __is_old_image = False
    __capture_thread: Thread | None
    __stop_thread = Event()

    def _read_action(self, autosplit: AutoSplit) -> tuple[cv2.Mat | None, bool]:
        raise NotImplementedError

    def __read_loop(self, autosplit: AutoSplit):
        try:
            while not self.__stop_thread.is_set():
                self._last_captured_frame, self.__is_old_image = self._read_action(autosplit)
        except Exception as exception:  # noqa: BLE001 # We really want to catch everything here
            error = exception
            autosplit.show_error_signal.emit(
                lambda: error_messages.exception_traceback(
                    error,
                    "AutoSplit encountered an unhandled exception while "
                    + "trying to grab a frame and has stopped capture. "
                    + error_messages.CREATE_NEW_ISSUE_MESSAGE,
                ),
            )
            self.close(autosplit, from_exception=True)

    def __init__(self, autosplit: AutoSplit):
        self.__stop_thread = Event()
        self.__capture_thread = Thread(target=self.__read_loop, args=(autosplit,))
        self.__capture_thread.start()
        super().__init__()

    def close(self, autosplit: AutoSplit, from_exception: bool = False):
        self.__stop_thread.set()
        if self.__capture_thread and not from_exception:
            self.__capture_thread.join()
            self.__capture_thread = None

    def get_frame(self, autosplit: AutoSplit) -> tuple[cv2.Mat | None, bool]:
        if not self.check_selected_region_exists(autosplit):
            return None, False

        image = self._last_captured_frame
        is_old_image = self.__is_old_image
        self.__is_old_image = True
        return image, is_old_image
