from dataclasses import dataclass
from platform import version
from collections import OrderedDict
from enum import Enum, EnumMeta, unique

import cv2


# https://docs.microsoft.com/en-us/uwp/api/windows.graphics.capture.graphicscapturepicker#applies-to
WCG_MIN_BUILD = 999999  # TODO: Change to 17134 once implemented


@dataclass
class DisplayCaptureMethodInfo():
    name: str
    short_description: str
    description: str


class DisplayCaptureMethodMeta(EnumMeta):
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
class DisplayCaptureMethod(Enum, metaclass=DisplayCaptureMethodMeta):
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


class DisplayCaptureMethodDict(OrderedDict[DisplayCaptureMethod, DisplayCaptureMethodInfo]):
    def get_method_by_index(self, index: int):
        return list(self.keys())[index]


DISPLAY_CAPTURE_METHODS = DisplayCaptureMethodDict({
    DisplayCaptureMethod.BITBLT: DisplayCaptureMethodInfo(
        name="BitBlt",
        short_description="fast, issues with Hardware Acceleration and OpenGL",
        description=(
            "\nA good default fast option. Allows recording background windows "
            "\n(as long as they still decide to render in the background), "
            "\nbut it cannot properly record OpenGL or Hardware Accelerated Windows. "
        ),
    ),
    DisplayCaptureMethod.WINDOWS_GRAPHICS_CAPTURE: DisplayCaptureMethodInfo(
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
    DisplayCaptureMethod.DESKTOP_DUPLICATION: DisplayCaptureMethodInfo(
        name="Direct3D Desktop Duplication",
        short_description="very slow, bound to display",
        description=(
            "\nDuplicates the desktop using Direct3D. "
            "\nIt can record OpenGL and Hardware Accelerated windows. "
            "\nBut it's about 10-15x slower than BitBlt, "
            "\noverlapping windows will show up and can't record across displays. "
        ),
    ),
    DisplayCaptureMethod.PRINTWINDOW_RENDERFULLCONTENT: DisplayCaptureMethodInfo(
        name="Force Full Content Rendering",
        short_description="very slow, can affect rendering pipeline",
        description=(
            "\nUses BitBlt behind the scene, but passes a special flag "
            "\nto PrintWindow to force rendering the entire desktop window. "
            "\nAbout 10-15x slower than BitBlt based on window size "
            "\nand can mess up some applications' rendering pipelines. "
        ),
    ),
})


# Detect and remove unsupported capture methods
if int(version().split(".")[2]) < WCG_MIN_BUILD:
    DISPLAY_CAPTURE_METHODS.pop(DisplayCaptureMethod.WINDOWS_GRAPHICS_CAPTURE)


@dataclass
class CameraInfo():
    id: int
    name: str
    occupied: str


def get_all_cameras():
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


# Detect and remove unsupported capture methods
if int(version().split(".")[2]) < WCG_MIN_BUILD:
    DISPLAY_CAPTURE_METHODS.pop(DisplayCaptureMethod.WINDOWS_GRAPHICS_CAPTURE)
