import sys
from typing import TYPE_CHECKING

import cv2
import cv2.Error
import numpy as np
from cv2.typing import MatLike
from typing_extensions import override

from capture_method.CaptureMethodBase import ThreadedLoopCaptureMethod
from utils import ImageShape, is_valid_image

if sys.platform == "win32":
    from pygrabber.dshow_graph import FilterGraph

if TYPE_CHECKING:
    from AutoSplit import AutoSplit

OBS_VIRTUALCAM_PLUGIN_BLANK_PIXEL = (127, 129, 128)


def is_blank(image: MatLike):
    # Running np.all on the entire array or looping manually through the
    # entire array is extremely slow when we can't stop early.
    # Instead we check for a few key pixels, in this case, corners
    return np.all(
        image[
            :: image.shape[ImageShape.Y] - 1,
            :: image.shape[ImageShape.X] - 1,
        ]
        == OBS_VIRTUALCAM_PLUGIN_BLANK_PIXEL,
    )


class VideoCaptureDeviceCaptureMethod(ThreadedLoopCaptureMethod):
    name = "Video Capture Device"
    short_description = "see below"
    description = (
        "\nUses a Video Capture Device, like a webcam, virtual cam, or capture card. "
        + "\nYou can select one below. "
    )
    window_recovery_message = "Waiting for capture device..."

    capture_device: cv2.VideoCapture

    def __init__(self, autosplit: "AutoSplit"):
        super().__init__(autosplit)
        self.capture_device = cv2.VideoCapture(autosplit.settings_dict["capture_device_id"])
        self.capture_device.setExceptionMode(True)

        # The video capture device isn't accessible, don't bother with it.
        if not self.capture_device.isOpened():
            self.close()
            return

        # Ensure we're using the right camera size. And not OpenCV's default 640x480
        if sys.platform == "win32":
            filter_graph = FilterGraph()
            filter_graph.add_video_input_device(autosplit.settings_dict["capture_device_id"])
            width, height = filter_graph.get_input_device().get_current_format()
            filter_graph.remove_filters()
            try:
                self.capture_device.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                self.capture_device.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            except cv2.error:
                # Some cameras don't allow changing the resolution
                pass

    @override
    def close(self):
        super().close()
        self.capture_device.release()

    @override
    def _read_action(self):
        try:
            result, image = self.capture_device.read()
        except cv2.error as cv2_error:
            if not (
                cv2_error.code == cv2.Error.STS_ERROR
                and (
                    # Likely means the camera is occupied OR the camera index is out of range (like -1)
                    cv2_error.msg.endswith("in function 'cv::VideoCapture::grab'\n")
                    # Some capture cards we cannot use directly
                    # https://github.com/opencv/opencv/issues/23539
                    or cv2_error.msg.endswith("in function 'cv::VideoCapture::retrieve'\n")
                )
            ):
                raise
            return None

        if not result or not is_valid_image(image) or is_blank(image):
            return None

        selection = self._autosplit_ref.settings_dict["capture_region"]
        # Ensure we can't go OOB of the image
        y = min(selection["y"], image.shape[ImageShape.Y] - 1)
        x = min(selection["x"], image.shape[ImageShape.X] - 1)
        image = image[
            y : y + selection["height"],
            x : x + selection["width"],
        ]
        return cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)

    @override
    def check_selected_region_exists(self):
        return bool(self.capture_device.isOpened())
