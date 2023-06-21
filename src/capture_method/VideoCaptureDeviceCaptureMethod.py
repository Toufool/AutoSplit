from __future__ import annotations

from dataclasses import dataclass
from threading import Event, Thread
from typing import TYPE_CHECKING

import cv2
import cv2.Error
import numpy as np
from device import getDeviceList
from typing_extensions import override

from capture_method.CaptureMethodBase import CaptureMethodBase
from error_messages import CREATE_NEW_ISSUE_MESSAGE, exception_traceback
from utils import ImageShape, is_valid_image

if TYPE_CHECKING:
    import cv2.typing

    from AutoSplit import AutoSplit

OBS_VIRTUALCAM_PLUGIN_BLANK_PIXEL = [127, 129, 128]


def is_blank(image: cv2.typing.MatLike):
    # Running np.all on the entire array or looping manually through the
    # entire array is extremely slow when we can't stop early.
    # Instead we check for a few key pixels, in this case, corners
    return np.all(
        image[
            ::image.shape[ImageShape.Y] - 1,
            ::image.shape[ImageShape.X] - 1,
        ] == OBS_VIRTUALCAM_PLUGIN_BLANK_PIXEL,
    )


class VideoCaptureDeviceCaptureMethod(CaptureMethodBase):
    name = "Video Capture Device"
    short_description = "see below"
    description = (
        "\nUses a Video Capture Device, like a webcam, virtual cam, or capture card. "
        + "\nYou can select one below. "
    )

    capture_device: cv2.VideoCapture
    capture_thread: Thread | None
    stop_thread: Event
    last_captured_frame: cv2.typing.MatLike | None = None
    is_old_image = False

    def __read_loop(self, autosplit: AutoSplit):
        try:
            while not self.stop_thread.is_set():
                try:
                    result, image = self.capture_device.read()
                except cv2.error as error:
                    if not (
                        error.code == cv2.Error.STS_ERROR
                        and (
                            # Likely means the camera is occupied
                            error.msg.endswith("in function 'cv::VideoCapture::grab'\n")
                            # Some capture cards we cannot use directly
                            # https://github.com/opencv/opencv/issues/23539
                            or error.msg.endswith("in function 'cv::VideoCapture::retrieve'\n")
                        )
                    ):
                        raise
                    result = False
                    image = None
                if not result:
                    image = None

                # Blank frame. Reuse the previous one.
                if image is not None and is_blank(image):
                    continue

                self.last_captured_frame = image
                self.is_old_image = False
        except Exception as exception:  # noqa: BLE001 # We really want to catch everything here
            error = exception
            self.capture_device.release()
            autosplit.show_error_signal.emit(
                lambda: exception_traceback(
                    error,
                    "AutoSplit encountered an unhandled exception while "
                    + "trying to grab a frame and has stopped capture. "
                    + CREATE_NEW_ISSUE_MESSAGE,
                ),
            )

    def __init__(self, autosplit: AutoSplit):
        super().__init__(autosplit)

        self.capture_device = cv2.VideoCapture(autosplit.settings_dict["capture_device_id"])
        self.capture_device.setExceptionMode(True)

        width, height = get_all_video_capture_devices()[autosplit.settings_dict["capture_device_id"]].resolution
        # https://github.com/opencv/opencv/issues/17012
        # Ensure we're using the right camera size. And not OpenCV's default 640x480
        try:
            self.capture_device.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.capture_device.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        except cv2.error:
            # Some cameras don't allow changing the resolution
            pass
        self.stop_thread = Event()
        self.capture_thread = Thread(target=lambda: self.__read_loop(autosplit))
        self.capture_thread.start()

    @override
    def close(self, autosplit: AutoSplit):
        self.stop_thread.set()
        if self.capture_thread:
            self.capture_thread.join()
            self.capture_thread = None
        self.capture_device.release()

    @override
    def get_frame(self, autosplit: AutoSplit):
        if not self.check_selected_region_exists(autosplit):
            return None, False

        image = self.last_captured_frame
        is_old_image = self.is_old_image
        self.is_old_image = True
        if not is_valid_image(image):
            return None, is_old_image

        selection = autosplit.settings_dict["capture_region"]
        # Ensure we can't go OOB of the image
        y = min(selection["y"], image.shape[ImageShape.Y] - 1)
        x = min(selection["x"], image.shape[ImageShape.X] - 1)
        image = image[
            y:y + selection["height"],
            x:x + selection["width"],
        ]
        return cv2.cvtColor(image, cv2.COLOR_BGR2BGRA), is_old_image

    @override
    def check_selected_region_exists(self, autosplit: AutoSplit):
        return bool(self.capture_device.isOpened())


@dataclass
class CameraInfo:
    device_id: int
    name: str
    occupied: bool
    backend: str
    resolution: tuple[int, int]


def get_all_video_capture_devices() -> list[CameraInfo]:
    named_video_inputs = getDeviceList()

    # async def get_camera_info(index: int, device_name: str, resolution: tuple[int, int]):
    #     backend = ""
    #     occupied = False
    #     # Probing freezes some devices (like GV-USB2 and AverMedia) if already in use
    #     # #169
    #     # FIXME: Maybe offer the option to the user to obtain more info about their devies?
    #     #        Off by default. With a tooltip to explain the risk.
    #     # video_capture = cv2.VideoCapture(index)
    #     # video_capture.setExceptionMode(True)
    #     # try:
    #     #     # https://docs.opencv.org/3.4/d4/d15/group__videoio__flags__base.html#ga023786be1ee68a9105bf2e48c700294d
    #     #     backend = video_capture.getBackendName()  # STS_ASSERT
    #     #     video_capture.grab()  # STS_ERROR
    #     # except cv2.error as error:
    #     #     return CameraInfo(index, device_name, True, backend) \
    #     #         if error.code in (cv2.Error.STS_ERROR, cv2.Error.STS_ASSERT) \
    #     #         else None
    #     # finally:
    #     #     video_capture.release()

    #     return CameraInfo(index, device_name, occupied, backend, resolution)

    # # Note: Return type required https://github.com/python/typeshed/issues/2652
    # future = asyncio.gather(
    #     *[
    #         get_camera_info(index, info[0], info[1][0]) for index, info
    #         in enumerate(named_video_inputs)
    #     ],
    # )

    # return [
    #     camera_info for camera_info
    #     in await future
    #     if camera_info is not None
    # ]

    return [CameraInfo(index, info[0], False, "", info[1][0]) for index, info in enumerate(named_video_inputs)]
