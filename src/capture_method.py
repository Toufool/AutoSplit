from collections import OrderedDict
from enum import Enum, unique
from platform import version
from typing import TypedDict

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
        short_description="fastest, least compatible",
        description=(
            "\nA good default fast option. Also allows recording background windows "
            "\n(as long as they still actually render when in the background), but it "
            "\ncannot properly record OpenGL, Hardware Accelerated or Exclusive Fullscreen windows. "
            "\nThe smaller the region, the more efficient it is. "
        ),
    ),
    CaptureMethod.WINDOWS_GRAPHICS_CAPTURE: CaptureMethodInfo(
        name="Windows Graphics Capture",
        short_description="fast, most compatible but less features",
        description=(
            f"\nOnly available in Windows 10.0.{WCG_MIN_BUILD} and up. "
            "\nAllows recording UWP apps, Hardware Accelerated and Exclusive Fullscreen windows. "
            "\nCaps at around 60 FPS. "
        ),
    ),
    CaptureMethod.DESKTOP_DUPLICATION: CaptureMethodInfo(
        name="Direct3D Desktop Duplication",
        short_description="slower, bound to display",
        description=(
            "\nDuplicates the desktop using Direct3D. "
            "\nIt can record OpenGL and Hardware Accelerated windows. "
            "\nAbout 10-15x slower than BitBlt. Not affected by window size. "
            "\noverlapping windows will show up and can't record across displays. "
        ),
    ),
    CaptureMethod.PRINTWINDOW_RENDERFULLCONTENT: CaptureMethodInfo(
        name="Force Full Content Rendering",
        short_description="very slow, can affect rendering pipeline",
        description=(
            "\nUses BitBlt behind the scene, but passes a special flag "
            "\nto PrintWindow to force rendering the entire desktop. "
            "\nAbout 10-15x slower than BitBlt based on original window size "
            "\nand can mess up some applications' rendering pipelines. "
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
    CAPTURE_METHODS.pop(CaptureMethod.WINDOWS_GRAPHICS_CAPTURE)
