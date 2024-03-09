from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import TYPE_CHECKING, ClassVar, final

from cv2.typing import MatLike
from PySide6 import QtCore
from typing_extensions import override

import error_messages
from utils import ONE_SECOND, QTIMER_FPS_LIMIT, is_valid_hwnd, is_valid_image

if TYPE_CHECKING:
    from AutoSplit import AutoSplit


class CaptureMethodBase:
    name = "None"
    short_description = ""
    description = ""
    window_recovery_message = "Trying to recover window..."

    last_captured_image: MatLike | None = None
    _autosplit_ref: "AutoSplit"
    # Making _subscriptions a ClassVar ensures the state will be shared across Methods
    _subscriptions: ClassVar = set[Callable[[MatLike | None], object]]()

    def __init__(self, autosplit: "AutoSplit"):
        self._autosplit_ref = autosplit

    def reinitialize(self):
        self.close()
        self.__init__(self._autosplit_ref)  # type: ignore[misc]  # noqa: PLC2801

    def close(self):
        # Some capture methods don't need any cleanup
        pass

    def set_fps_limit(self, fps: int):
        # CaptureMethodBase doesn't actually record. This is implemented by child classes
        pass

    def recover_window(self, captured_window_title: str) -> bool:  # noqa: PLR6301
        # Some capture methods can't "recover" and must simply wait
        return False

    def check_selected_region_exists(self) -> bool:
        return is_valid_hwnd(self._autosplit_ref.hwnd)

    def subscribe_to_new_frame(self, callback: Callable[[MatLike | None], object]):
        self._subscriptions.add(callback)

    def unsubscribe_from_new_frame(self, callback: Callable[[MatLike | None], object]):
        try:
            self._subscriptions.remove(callback)
        except KeyError:
            pass

    @final
    def _push_new_frame_to_subscribers(self, frame: MatLike | None):
        for subscription in self._subscriptions:
            subscription(frame)


class ThreadedLoopCaptureMethod(CaptureMethodBase, ABC):
    def __init__(self, autosplit: "AutoSplit"):
        super().__init__(autosplit)
        self.__capture_timer = QtCore.QTimer()
        self.__capture_timer.setTimerType(QtCore.Qt.TimerType.PreciseTimer)
        self.__capture_timer.timeout.connect(self.__read_loop)
        self.__capture_timer.start(int(ONE_SECOND / self._autosplit_ref.settings_dict["fps_limit"]))

    @override
    def close(self):
        self.__capture_timer.stop()

    @override
    def set_fps_limit(self, fps: int):
        if fps > QTIMER_FPS_LIMIT:
            raise ValueError(f"QTimer supports a resolution of maximum {QTIMER_FPS_LIMIT} FPS")
        if fps < 0:
            raise ValueError("'fps' must be positive or 0")
        interval = 0 if fps == 0 else int(ONE_SECOND / fps)
        self.__capture_timer.setInterval(interval)

    @abstractmethod
    def _read_action(self) -> MatLike | None:
        """The synchronous code that requests a new image from the operating system."""
        raise NotImplementedError

    @final
    def __read_loop(self):
        # Very useful debug print
        # print("subscriptions:", len(self._subscriptions), [x.__name__ for x in self._subscriptions])
        if len(self._subscriptions) == 0:
            # optimisation on idle: no subscriber means no work needed
            return
        try:
            captured_image = None
            if self.check_selected_region_exists():
                captured_image = self._read_action()
                # HACK: When WindowsGraphicsCaptureMethod tries to get images too quickly,
                # it'll return the previous image directly to avoid looking like it dropped signal
                if captured_image is not self.last_captured_image:
                    self.last_captured_image = captured_image
                    self._push_new_frame_to_subscribers(self.last_captured_image)
            else:
                self.last_captured_image = None
                self._push_new_frame_to_subscribers(None)

            # This most likely means we lost capture
            # (ie the captured window was closed, crashed, lost capture device, etc.)
            if not is_valid_image(captured_image):
                # Try to recover by using the window name
                self._autosplit_ref.live_image.setText(self.window_recovery_message)
                recovered = self._autosplit_ref.capture_method.recover_window(
                    self._autosplit_ref.settings_dict["captured_window_title"],
                )
                if recovered and not self._autosplit_ref.settings_dict["live_capture_region"]:
                    self._autosplit_ref.live_image.setText("Live Capture Region hidden")
        except Exception as exception:  # noqa: BLE001 # We really want to catch everything here
            error = exception
            self._autosplit_ref.show_error_signal.emit(
                lambda: error_messages.exception_traceback(
                    error,
                    "AutoSplit encountered an unhandled exception while "
                    + "trying to grab a frame and has stopped capture. "
                    + error_messages.CREATE_NEW_ISSUE_MESSAGE,
                ),
            )
            self.close()
