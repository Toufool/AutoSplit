import sys

if sys.platform != "linux":
    raise OSError
from typing import TYPE_CHECKING, cast, override

import numpy as np
from PySide6.QtCore import QBuffer, QIODeviceBase
from PySide6.QtGui import QGuiApplication

from capture_method.CaptureMethodBase import CaptureMethodBase

if TYPE_CHECKING:
    from cv2.typing import MatLike


class QtCaptureMethod(CaptureMethodBase):
    _render_full_content = False

    @override
    def get_frame(self):
        if not self.check_selected_region_exists():
            return None

        buffer = QBuffer()
        buffer.open(QIODeviceBase.OpenModeFlag.ReadWrite)
        winid = self._autosplit_ref.winId()
        test = QGuiApplication.primaryScreen().grabWindow(winid, 0, 0, 200, 200)
        image = test.toImage()
        b = image.bits()
        # sip.voidptr must know size to support python buffer interface
        # b.setsize(200 * 200 * 3)
        frame = np.frombuffer(cast("MatLike", b), np.uint8).reshape((200, 200, 3))

        # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return frame  # noqa: RET504
