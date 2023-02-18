from __future__ import annotations

import asyncio
from collections import OrderedDict
from dataclasses import dataclass
from enum import Enum, EnumMeta, unique
from typing import TYPE_CHECKING, TypedDict, cast

from pygrabber.dshow_graph import FilterGraph

from capture_method.BitBltCaptureMethod import BitBltCaptureMethod
from capture_method.CaptureMethodBase import CaptureMethodBase
from capture_method.DesktopDuplicationCaptureMethod import DesktopDuplicationCaptureMethod
from capture_method.ForceFullContentRenderingCaptureMethod import ForceFullContentRenderingCaptureMethod
from capture_method.VideoCaptureDeviceCaptureMethod import VideoCaptureDeviceCaptureMethod
from capture_method.WindowsGraphicsCaptureMethod import WindowsGraphicsCaptureMethod
from utils import WINDOWS_BUILD_NUMBER, first, try_get_direct3d_device

if TYPE_CHECKING:
    from AutoSplit import AutoSplit

WGC_MIN_BUILD = 17134
"""https://docs.microsoft.com/en-us/uwp/api/windows.graphics.capture.graphicscapturepicker#applies-to"""
LEARNING_MODE_DEVICE_BUILD = 17763
"""https://learn.microsoft.com/en-us/uwp/api/windows.ai.machinelearning.learningmodeldevice"""


class Region(TypedDict):
    x: int
    y: int
    width: int
    height: int


@dataclass
class CaptureMethodInfo():
    name: str
    short_description: str
    description: str
    implementation: type[CaptureMethodBase]


class CaptureMethodMeta(EnumMeta):
    # Allow checking if simple string is enum
    def __contains__(self, other: str):
        try:
            self(other)  # pyright: ignore [reportGeneralTypeIssues] pylint: disable=no-value-for-parameter
        except ValueError:
            return False
        else:
            return True


@unique
class CaptureMethodEnum(Enum, metaclass=CaptureMethodMeta):
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

    NONE = ""
    BITBLT = "BITBLT"
    WINDOWS_GRAPHICS_CAPTURE = "WINDOWS_GRAPHICS_CAPTURE"
    PRINTWINDOW_RENDERFULLCONTENT = "PRINTWINDOW_RENDERFULLCONTENT"
    DESKTOP_DUPLICATION = "DESKTOP_DUPLICATION"
    VIDEO_CAPTURE_DEVICE = "VIDEO_CAPTURE_DEVICE"


class CaptureMethodDict(OrderedDict[CaptureMethodEnum, CaptureMethodInfo]):
    def get_index(self, capture_method: str | CaptureMethodEnum):
        """
        Returns 0 if the capture_method is invalid or unsupported
        """
        try:
            return list(self.keys()).index(cast(CaptureMethodEnum, capture_method))
        except ValueError:
            return 0

    def get_method_by_index(self, index: int):
        """
        Returns the `CaptureMethodEnum` at index.
        If index is invalid, returns the first (default) `CaptureMethodEnum`.
        Returns `CaptureMethodEnum.NONE` if there are no capture methods available.
        """
        if len(self) <= 0:
            return CaptureMethodEnum.NONE
        if index <= 0:
            return first(self)
        return list(self.keys())[index]

    if TYPE_CHECKING:  # noqa: CCE002
        __getitem__ = None  # pyright: ignore[reportGeneralTypeIssues]  # Disallow unsafe get

    def get(self, __key: CaptureMethodEnum):
        """
        Returns the `CaptureMethodInfo` for `CaptureMethodEnum` if `CaptureMethodEnum` is available,
        else defaults to the first available `CaptureMethodEnum`.
        Returns the `CaptureMethodBase` (default) implementation if there's no capture methods.
        """
        if __key == CaptureMethodEnum.NONE or len(self) <= 0:
            return NONE_CAPTURE_METHOD
        return super().get(__key, first(self.values()))


NONE_CAPTURE_METHOD = CaptureMethodInfo(
    name="None",
    short_description="",
    description="",
    implementation=CaptureMethodBase,
)

CAPTURE_METHODS = CaptureMethodDict()
if (  # Windows Graphics Capture requires a minimum Windows Build
    WINDOWS_BUILD_NUMBER >= WGC_MIN_BUILD
    # Our current implementation of Windows Graphics Capture does not ensure we can get an ID3DDevice
    and try_get_direct3d_device()
):
    CAPTURE_METHODS[CaptureMethodEnum.WINDOWS_GRAPHICS_CAPTURE] = CaptureMethodInfo(
        name="Windows Graphics Capture",
        short_description="fast, most compatible, capped at 60fps",
        description=(
            f"\nOnly available in Windows 10.0.{WGC_MIN_BUILD} and up. "
            f"\nDue to current technical limitations, Windows versions below 10.0.0.{LEARNING_MODE_DEVICE_BUILD}"
            "\nrequire having at least one audio or video Capture Device connected and enabled."
            "\nAllows recording UWP apps, Hardware Accelerated and Exclusive Fullscreen windows. "
            "\nAdds a yellow border on Windows 10 (not on Windows 11)."
            "\nCaps at around 60 FPS. "
        ),
        implementation=WindowsGraphicsCaptureMethod,
    )
CAPTURE_METHODS[CaptureMethodEnum.BITBLT] = CaptureMethodInfo(
    name="BitBlt",
    short_description="fastest, least compatible",
    description=(
        "\nThe best option when compatible. But it cannot properly record "
        "\nOpenGL, Hardware Accelerated or Exclusive Fullscreen windows. "
        "\nThe smaller the selected region, the more efficient it is. "
    ),

    implementation=BitBltCaptureMethod,
)
CAPTURE_METHODS[CaptureMethodEnum.DESKTOP_DUPLICATION] = CaptureMethodInfo(
    name="Direct3D Desktop Duplication",
    short_description="slower, bound to display",
    description=(
        "\nDuplicates the desktop using Direct3D. "
        "\nIt can record OpenGL and Hardware Accelerated windows. "
        "\nAbout 10-15x slower than BitBlt. Not affected by window size. "
        "\nOverlapping windows will show up and can't record across displays. "
    ),
    implementation=DesktopDuplicationCaptureMethod,
)
CAPTURE_METHODS[CaptureMethodEnum.PRINTWINDOW_RENDERFULLCONTENT] = CaptureMethodInfo(
    name="Force Full Content Rendering",
    short_description="very slow, can affect rendering pipeline",
    description=(
        "\nUses BitBlt behind the scene, but passes a special flag "
        "\nto PrintWindow to force rendering the entire desktop. "
        "\nAbout 10-15x slower than BitBlt based on original window size "
        "\nand can mess up some applications' rendering pipelines. "
    ),
    implementation=ForceFullContentRenderingCaptureMethod,
)
CAPTURE_METHODS[CaptureMethodEnum.VIDEO_CAPTURE_DEVICE] = CaptureMethodInfo(
    name="Video Capture Device",
    short_description="see below",
    description=(
        "\nUses a Video Capture Device, like a webcam, virtual cam, or capture card. "
        "\nYou can select one below. "
        "\nThere are currently performance issues, but it might be more convenient. "
        "\nIf you want to use this with OBS' Virtual Camera, use the Virtualcam plugin instead "
        "\nhttps://github.com/Avasam/obs-virtual-cam/releases"
    ),
    implementation=VideoCaptureDeviceCaptureMethod,
)


def change_capture_method(selected_capture_method: CaptureMethodEnum, autosplit: AutoSplit):
    autosplit.capture_method.close(autosplit)
    autosplit.capture_method = CAPTURE_METHODS.get(selected_capture_method).implementation(autosplit)
    if selected_capture_method == CaptureMethodEnum.VIDEO_CAPTURE_DEVICE:
        autosplit.select_region_button.setDisabled(True)
        autosplit.select_window_button.setDisabled(True)
    else:
        autosplit.select_region_button.setDisabled(False)
        autosplit.select_window_button.setDisabled(False)


@dataclass
class CameraInfo():
    device_id: int
    name: str
    occupied: bool
    backend: str
    resolution: tuple[int, int] | None


def get_input_device_resolution(index: int):
    filter_graph = FilterGraph()
    filter_graph.add_video_input_device(index)
    resolution = filter_graph.get_input_device().get_current_format()
    filter_graph.remove_filters()
    return resolution


async def get_all_video_capture_devices() -> list[CameraInfo]:
    named_video_inputs = FilterGraph().get_input_devices()

    async def get_camera_info(index: int, device_name: str):
        backend = ""
        # Probing freezes some devices (like GV-USB2 and AverMedia) if already in use
        # #169
        # FIXME: Maybe offer the option to the user to obtain more info about their devies?
        #        Off by default. With a tooltip to explain the risk.
        # video_capture = cv2.VideoCapture(index)
        # video_capture.setExceptionMode(True)
        # try:
        #     # https://docs.opencv.org/3.4/d4/d15/group__videoio__flags__base.html#ga023786be1ee68a9105bf2e48c700294d
        #     backend = video_capture.getBackendName()  # STS_ASSERT
        #     video_capture.grab()  # STS_ERROR
        # except cv2.error as error:
        #     return CameraInfo(index, device_name, True, backend) \
        #         if error.code in (cv2.Error.STS_ERROR, cv2.Error.STS_ASSERT) \
        #         else None
        # finally:
        #     video_capture.release()

        return CameraInfo(index, device_name, False, backend, get_input_device_resolution(index))

    future = asyncio.gather(
        *[
            get_camera_info(index, name) for index, name
            in enumerate(named_video_inputs)
        ],
    )

    return [
        camera_info for camera_info
        in await future
        if camera_info is not None
    ]
