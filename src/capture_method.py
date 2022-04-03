from typing import TypedDict

from platform import version
from collections import OrderedDict
from enum import Enum, unique
# https://docs.microsoft.com/en-us/uwp/api/windows.graphics.capture.graphicscapturepicker#applies-to
WCG_MIN_BUILD = 17134


class CaptureMethodInfo(TypedDict):
    name: str
    short_description: str
    description: str


@unique
class CaptureMethod(Enum):
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


CAPTURE_METHODS = OrderedDict({
    CaptureMethod.BITBLT: CaptureMethodInfo(
        name="BitBlt",
        short_description="fast, issues with Hardware Acceleration and OpenGL",
        description=(
            "A good default fast option. Allows recording background windows "
            "(as long as they still decide to render in the background), "
            "but it cannot properly record OpenGL or Hardware Accelerated Windows."
        ),
    ),
    CaptureMethod.WINDOWS_GRAPHICS_CAPTURE: CaptureMethodInfo(
        name="Windows Graphics Capture",
        short_description="Windows 10 {WCG_MIN_BUILD} and up, most compatible if available",
        description=(
            "Only available in recent Windows updates. Allows recording UWP apps "
            "(hardware accelerated and fullscreen exclusives? To be tested). "
            "Adds a yellow border around the recorded window."
        ),
    ),
    CaptureMethod.DESKTOP_DUPLICATION: CaptureMethodInfo(
        name="Direct3D Desktop Duplication",
        short_description="very slow, bound to display, supports OpenGL and DirectX 11/12 exclusive fullscreen",
        description=(
            "Duplicates the desktop using Direct3D. It can record OpenGL and Hardware Accelerated windows. "
            "But it's about 10-15x slower than BitBlt, "
            "overlapping windows will show up and can't record across displays."
        ),
    ),
    CaptureMethod.PRINTWINDOW_RENDERFULLCONTENT: CaptureMethodInfo(
        name="Force Full Content Rendering",
        short_description="very slow, can affect rendering pipeline",
        description=(
            "Uses BitBlt behind the scene, but passes a special flag to PrintWindow to force rendering the "
            "entire desktop window. About 10-15x slower than BitBlt based on window size and can mess up some "
            "applications' rendering pipelines."
        ),
    ),
})


def get_capture_method_index(capture_method: CaptureMethod):
    """
    Returns 0 if the capture_method is invalid or unsupported
    """
    try:
        return list(CAPTURE_METHODS.keys()).index(capture_method)
    except ValueError:
        return 0


def get_capture_method_by_index(index: int):
    return list(CAPTURE_METHODS.keys())[index]


# Detect and remove unsupported capture methods
if int(version().split(".")[2]) < WCG_MIN_BUILD:
    CAPTURE_METHODS.pop(CaptureMethod.WINDOWS_GRAPHICS_CAPTURE)  # Not yet implemented
