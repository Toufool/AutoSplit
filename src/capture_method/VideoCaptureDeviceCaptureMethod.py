from __future__ import annotations

from typing import TYPE_CHECKING

import cv2

from capture_method.interface import CaptureMethodInterface

if TYPE_CHECKING:
    from AutoSplit import AutoSplit


class VideoCaptureDeviceCaptureMethod(CaptureMethodInterface):  # pylint: disable=too-few-public-methods
    capture_device: cv2.VideoCapture

    def __init__(self, autosplit: AutoSplit):
        super().__init__()
        self.capture_device = cv2.VideoCapture(autosplit.settings_dict["capture_device_id"])
        self.capture_device.setExceptionMode(True)

    def close(self, autosplit: AutoSplit):
        self.capture_device.release()

    def get_frame(self, autosplit: AutoSplit):
        selection = autosplit.settings_dict["capture_region"]
        if not self.check_selected_region_exists(autosplit):
            return None, False
        result, image = self.capture_device.read()
        if not result:
            return None, False
        # Ensure we can't go OOB of the image
        y = min(selection["y"], image.shape[0] - 1)
        x = min(selection["x"], image.shape[1] - 1)
        image = image[
            y:y + selection["height"],
            x:x + selection["width"],
        ]
        return cv2.cvtColor(image, cv2.COLOR_BGR2BGRA), False

    def check_selected_region_exists(self, autosplit: AutoSplit):
        return bool(self.capture_device.isOpened())
