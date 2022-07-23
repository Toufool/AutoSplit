from __future__ import annotations

import asyncio
from collections import OrderedDict
from dataclasses import dataclass
from enum import Enum, EnumMeta, unique
from typing import TYPE_CHECKING, TypedDict

import cv2
from pygrabber.dshow_graph import FilterGraph
from winsdk.windows.media.capture import MediaCapture

from capture_method.BitBltCaptureMethod import BitBltCaptureMethod
from capture_method.DesktopDuplicationCaptureMethod import DesktopDuplicationCaptureMethod
from capture_method.ForceFullContentRenderingCaptureMethod import ForceFullContentRenderingCaptureMethod
from capture_method.interface import CaptureMethodInterface
from capture_method.VideoCaptureDeviceCaptureMethod import VideoCaptureDeviceCaptureMethod
from capture_method.WindowsGraphicsCaptureMethod import WindowsGraphicsCaptureMethod
from utils import WINDOWS_BUILD_NUMBER

if TYPE_CHECKING:
    from AutoSplit import AutoSplit

WGC_MIN_BUILD = 17134
"""https://docs.microsoft.com/en-us/uwp/api/windows.graphics.capture.graphicscapturepicker#applies-to"""


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
    implementation: type[CaptureMethodInterface]


class CaptureMethodMeta(EnumMeta):
    # Allow checking if simple string is enum
    def __contains__(self, other: str):
        try:
            self(other)  # pyright: ignore [reportGeneralTypeIssues]
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

    def get_method_by_index(self, index: int):
        if len(self) <= 0:
            return CaptureMethodEnum.NONE
        if index < 0:
            return next(iter(self))
        return list(self.keys())[index]

    def __getitem__(self, key: CaptureMethodEnum):
        if key == CaptureMethodEnum.NONE:
            return NONE_CAPTURE_METHOD
        try:
            return super().__getitem__(key)
        # If requested method does not exists...
        except KeyError:
            try:
                # ...fallback to the first one
                return super().__getitem__(self.get_method_by_index(0))
            except KeyError:
                # ...fallback to an empty capture method to avoid crashes
                return NONE_CAPTURE_METHOD


NONE_CAPTURE_METHOD = CaptureMethodInfo(
    name="None",
    short_description="",
    description="",
    implementation=CaptureMethodInterface
)

CAPTURE_METHODS = CaptureMethodDict({
    CaptureMethodEnum.BITBLT: CaptureMethodInfo(
        name="BitBlt",
        short_description="fastest, least compatible",
        description=(
            "\nA good default fast option. But it cannot properly record "
            "\nOpenGL, Hardware Accelerated or Exclusive Fullscreen windows. "
            "\nThe smaller the selected region, the more efficient it is. "
        ),

        implementation=BitBltCaptureMethod,
    ),
    CaptureMethodEnum.WINDOWS_GRAPHICS_CAPTURE: CaptureMethodInfo(
        name="Windows Graphics Capture",
        short_description="fast, most compatible, capped at 60fps",
        description=(
            f"\nOnly available in Windows 10.0.{WGC_MIN_BUILD} and up. "
            "\nDue to current technical limitations, it requires having at least one "
            "\naudio or video Capture Device connected and enabled. Even if it won't be used. "
            "\nAllows recording UWP apps, Hardware Accelerated and Exclusive Fullscreen windows. "
            "\nAdds a yellow border on Windows 10 (not on Windows 11)."
            "\nCaps at around 60 FPS. "
        ),
        implementation=WindowsGraphicsCaptureMethod,
    ),
    CaptureMethodEnum.DESKTOP_DUPLICATION: CaptureMethodInfo(
        name="Direct3D Desktop Duplication",
        short_description="slower, bound to display",
        description=(
            "\nDuplicates the desktop using Direct3D. "
            "\nIt can record OpenGL and Hardware Accelerated windows. "
            "\nAbout 10-15x slower than BitBlt. Not affected by window size. "
            "\nOverlapping windows will show up and can't record across displays. "
        ),
        implementation=DesktopDuplicationCaptureMethod,
    ),
    CaptureMethodEnum.PRINTWINDOW_RENDERFULLCONTENT: CaptureMethodInfo(
        name="Force Full Content Rendering",
        short_description="very slow, can affect rendering pipeline",
        description=(
            "\nUses BitBlt behind the scene, but passes a special flag "
            "\nto PrintWindow to force rendering the entire desktop. "
            "\nAbout 10-15x slower than BitBlt based on original window size "
            "\nand can mess up some applications' rendering pipelines. "
        ),
        implementation=ForceFullContentRenderingCaptureMethod,
    ),
    CaptureMethodEnum.VIDEO_CAPTURE_DEVICE: CaptureMethodInfo(
        name="Video Capture Device",
        short_description="see below",
        description=(
            "\nUses a Video Capture Device, like a webcam, virtual cam, or capture card. "
            "\nYou can select one below. "
            "\nThere are currently performance issues, but it might be more convenient. "
            "\nIf you want to use this with OBS' Virtual Camera, use the Virtualcam plugin instead "
            "\nhttps://obsproject.com/forum/resources/obs-virtualcam.949/."
        ),
        implementation=VideoCaptureDeviceCaptureMethod,
    ),
})


def test_for_media_capture():
    async def coroutine():
        return await (MediaCapture().initialize_async() or asyncio.sleep(0))
    try:
        asyncio.run(coroutine())
        return True
    except OSError:
        return False


# Detect and remove unsupported capture methods
if (  # Windows Graphics Capture requires a minimum Windows Build
    WINDOWS_BUILD_NUMBER < WGC_MIN_BUILD
    # Our current implementation of Windows Graphics Capture requires at least one CaptureDevice
    or not test_for_media_capture()
):
    CAPTURE_METHODS.pop(CaptureMethodEnum.WINDOWS_GRAPHICS_CAPTURE)


def change_capture_method(selected_capture_method: CaptureMethodEnum, autosplit: AutoSplit):
    autosplit.capture_method.close(autosplit)
    autosplit.capture_method = CAPTURE_METHODS[selected_capture_method].implementation(autosplit)
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


async def get_all_video_capture_devices() -> list[CameraInfo]:
    named_video_inputs = FilterGraph().get_input_devices()

    async def get_camera_info(index: int, device_name: str):
        video_capture = cv2.VideoCapture(index)
        video_capture.setExceptionMode(True)
        backend = ""
        try:
            # https://docs.opencv.org/3.4/d4/d15/group__videoio__flags__base.html#ga023786be1ee68a9105bf2e48c700294d
            backend = video_capture.getBackendName()
            video_capture.grab()
        except cv2.error as error:  # pyright: ignore [reportUnknownVariableType]
            return CameraInfo(index, device_name, True, backend) \
                if error.code in (cv2.Error.STS_ERROR, cv2.Error.STS_ASSERT) \
                else None
        finally:
            video_capture.release()
        return CameraInfo(index, device_name, False, backend)

    future = asyncio.gather(*[
        get_camera_info(index, name) for index, name
        in enumerate(named_video_inputs)
    ])

    return [
        camera_info for camera_info
        in await future
        if camera_info is not None]
