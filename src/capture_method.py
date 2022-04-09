from collections import OrderedDict
from dataclasses import dataclass
from enum import Enum, EnumMeta, unique
from platform import version

import cv2

# https://docs.microsoft.com/en-us/uwp/api/windows.graphics.capture.graphicscapturepicker#applies-to
WCG_MIN_BUILD = 17134


@dataclass
class DisplayCaptureMethodInfo():
    name: str
    short_description: str
    description: str


class CaptureMethodMeta(EnumMeta):
    # Allow checking if simple string is enum
    def __contains__(cls, other: str):  # noqa:N805
        try:
            # pyright: reportGeneralTypeIssues=false
            cls(other)  # pylint: disable=no-value-for-parameter
        except ValueError:
            return False
        else:
            return True


@unique
class CaptureMethod(Enum, metaclass=CaptureMethodMeta):
    # Allow TOML to save as a simple string
    def __repr__(self):
        return self.value
    __str__ = __repr__

    # Allow direct comparison with strings
    def __eq__(self, other: object):
        return self.value == other.__str__()

    # Restore hashing functionality
    def __hash__(self):
        return self.value.__hash__()

    BITBLT = "BITBLT"
    WINDOWS_GRAPHICS_CAPTURE = "WINDOWS_GRAPHICS_CAPTURE"
    PRINTWINDOW_RENDERFULLCONTENT = "PRINTWINDOW_RENDERFULLCONTENT"
    DESKTOP_DUPLICATION = "DESKTOP_DUPLICATION"
    VIDEO_CAPTURE_DEVICE = "VIDEO_CAPTURE_DEVICE"


class DisplayCaptureMethodDict(OrderedDict[CaptureMethod, DisplayCaptureMethodInfo]):
    def get_method_by_index(self, index: int):
        return list(self.keys())[index]


CAPTURE_METHODS = DisplayCaptureMethodDict({
    CaptureMethod.BITBLT: DisplayCaptureMethodInfo(
        name="BitBlt",
        short_description="fast, issues with Hardware Acceleration and OpenGL",
        description=(
            "\nA good default fast option. Allows recording background windows "
            "\n(as long as they still decide to render in the background), "
            "\nbut it cannot properly record OpenGL or Hardware Accelerated Windows. "
        ),
    ),
    CaptureMethod.WINDOWS_GRAPHICS_CAPTURE: DisplayCaptureMethodInfo(
        name="Windows Graphics Capture",
        short_description="fastest, most compatible but less features",
        description=(
            f"\nOnly available in Windows 10.0.{WCG_MIN_BUILD} and up. "
            "\nAllows recording UWP apps, hardware accelerated and fullscreen exclusive windows. "
            "\nAdds a yellow border around the recorded window. "
            "\nDoes not support automatically recovering closed Windows, manual cropping only, "
            "\nand you have to reselect the window everytime you open AutoSplit. "
            "\nSee https://github.com/pywinrt/python-winsdk/issues/5 "
            "\nfor more details about those restrictions."
        ),
    ),
    CaptureMethod.DESKTOP_DUPLICATION: DisplayCaptureMethodInfo(
        name="Direct3D Desktop Duplication",
        short_description="very slow, bound to display",
        description=(
            "\nDuplicates the desktop using Direct3D. "
            "\nIt can record OpenGL and Hardware Accelerated windows. "
            "\nBut it's about 10-15x slower than BitBlt, "
            "\noverlapping windows will show up and can't record across displays. "
        ),
    ),
    CaptureMethod.PRINTWINDOW_RENDERFULLCONTENT: DisplayCaptureMethodInfo(
        name="Force Full Content Rendering",
        short_description="very slow, can affect rendering pipeline",
        description=(
            "\nUses BitBlt behind the scene, but passes a special flag "
            "\nto PrintWindow to force rendering the entire desktop window. "
            "\nAbout 10-15x slower than BitBlt based on window size "
            "\nand can mess up some applications' rendering pipelines. "
        ),
    ),
    CaptureMethod.VIDEO_CAPTURE_DEVICE: DisplayCaptureMethodInfo(
        name="Video Capture Device",
        short_description="select below",
        description=(
            "\nUses a Video Capture Device, like a webcam, virtual cam, or capture card. "
            "\nYou can select one below. "
            "\nIt is not yet possible for us to display the device name"
        ),
    ),
})


# Detect and remove unsupported capture methods
if int(version().split(".")[2]) < WCG_MIN_BUILD:
    CAPTURE_METHODS.pop(CaptureMethod.WINDOWS_GRAPHICS_CAPTURE)


@dataclass
class CameraInfo():
    id: int
    name: str
    occupied: bool


def get_all_video_capture_devices():
    index = 0
    video_captures: list[CameraInfo] = []
    while index < 8:
        video_capture = cv2.VideoCapture(index)  # pyright: ignore
        video_capture.setExceptionMode(True)
        try:
            # https://docs.opencv.org/3.4/d4/d15/group__videoio__flags__base.html#ga023786be1ee68a9105bf2e48c700294d
            print(video_capture.getBackendName())  # pyright: ignore
            video_capture.grab()
        except cv2.error as error:  # pyright: ignore
            if error.code == cv2.Error.STS_ERROR:
                video_captures.append(CameraInfo(index, f"Camera {index}", False))
        else:
            video_captures.append(CameraInfo(index, f"Camera {index}", True))

        video_capture.release()
        index += 1
    return video_captures
