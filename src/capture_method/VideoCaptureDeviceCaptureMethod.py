from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import cv2
import numpy as np

import error_messages
from capture_method.CaptureMethodBase import ThreadedCaptureMethod
from utils import is_valid_image

if sys.platform == "win32":
    from pygrabber.dshow_graph import FilterGraph

if TYPE_CHECKING:
    from AutoSplit import AutoSplit

OBS_CAMERA_BLANK_PIXEL = [127, 129, 128]


def is_blank(image: cv2.Mat):
    # Running np.all on the entire array or looping manually through the
    # entire array is extremely slow when we can't stop early.
    # Instead we check for a few key pixels, in this case, corners
    return np.all(image[::image.shape[0] - 1, ::image.shape[1] - 1] == OBS_CAMERA_BLANK_PIXEL)


class VideoCaptureDeviceCaptureMethod(ThreadedCaptureMethod):
    name = "Video Capture Device"
    short_description = "see below"
    description = (
        "\nUses a Video Capture Device, like a webcam, virtual cam, or capture card. "
        + "\nYou can select one below. "
        + "\nIf you want to use this with OBS' Virtual Camera, use the Virtualcam plugin instead "
        + "\nhttps://github.com/Avasam/obs-virtual-cam/releases"
    )

    capture_device: cv2.VideoCapture

    def _read_action(self, autosplit: AutoSplit):
        result = False
        image = None
        try:
            result, image = self.capture_device.read()
        except cv2.error as error:
            # STS_ERROR most likely means the camera is occupied
            if not (
               error.code != cv2.Error.STS_ERROR
               and error.msg.endswith("in function 'cv::VideoCapture::grab'\n")
            ):
                raise
        except Exception as exception:  # noqa: BLE001 # We really want to catch everything here
            error = exception
            self.capture_device.release()
            autosplit.show_error_signal.emit(
                lambda: error_messages.exception_traceback(
                    error,
                    "AutoSplit encountered an unhandled exception while "
                    + "trying to grab a frame and has stopped capture. "
                    + error_messages.CREATE_NEW_ISSUE_MESSAGE,
                ),
            )
        if not result or not is_valid_image(image):
            return None, False
        # Blank frame: Reuse the previous one.
        if is_blank(image):
            return self._last_captured_frame, True
        return image, False

    def __init__(self, autosplit: AutoSplit):
        self.capture_device = cv2.VideoCapture(autosplit.settings_dict["capture_device_id"])
        self.capture_device.setExceptionMode(True)

        # Ensure we're using the right camera size. And not OpenCV's default 640x480
        if sys.platform == "win32":
            filter_graph = FilterGraph()
            filter_graph.add_video_input_device(autosplit.settings_dict["capture_device_id"])
            width, height = filter_graph.get_input_device().get_current_format()
            filter_graph.remove_filters()
            try:
                self.capture_device.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                self.capture_device.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            # Some cameras don't allow changing the resolution
            except cv2.error:
                pass

        super().__init__(autosplit)

    def close(self, autosplit: AutoSplit, from_exception: bool = False):
        super().close(autosplit, from_exception)
        self.capture_device.release()

    def get_frame(self, autosplit: AutoSplit):
        if not self.check_selected_region_exists(autosplit):
            return None, False

        image, is_old_image = super().get_frame(autosplit)
        if not is_valid_image(image):
            return None, is_old_image

        selection = autosplit.settings_dict["capture_region"]
        # Ensure we can't go OOB of the image
        y = min(selection["y"], image.shape[0] - 1)
        x = min(selection["x"], image.shape[1] - 1)
        image = image[
            y:y + selection["height"],
            x:x + selection["width"],
        ]
        return cv2.cvtColor(image, cv2.COLOR_BGR2BGRA), is_old_image

    def check_selected_region_exists(self, autosplit: AutoSplit):
        return bool(self.capture_device.isOpened())
