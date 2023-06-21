from __future__ import annotations

import asyncio
from collections import OrderedDict
from dataclasses import dataclass
from enum import Enum, EnumMeta, unique
from typing import TYPE_CHECKING, NoReturn, TypedDict, cast

from _ctypes import COMError
from pygrabber.dshow_graph import FilterGraph
from typing_extensions import Never, override

from capture_method.BitBltCaptureMethod import BitBltCaptureMethod
from capture_method.CaptureMethodBase import CaptureMethodBase
from capture_method.DesktopDuplicationCaptureMethod import DesktopDuplicationCaptureMethod
from capture_method.ForceFullContentRenderingCaptureMethod import ForceFullContentRenderingCaptureMethod
from capture_method.VideoCaptureDeviceCaptureMethod import VideoCaptureDeviceCaptureMethod
from capture_method.WindowsGraphicsCaptureMethod import WindowsGraphicsCaptureMethod
from utils import WGC_MIN_BUILD, WINDOWS_BUILD_NUMBER, first, try_get_direct3d_device

if TYPE_CHECKING:
    from AutoSplit import AutoSplit


class Region(TypedDict):
    x: int
    y: int
    width: int
    height: int


class CaptureMethodMeta(EnumMeta):
    # Allow checking if simple string is enum
    @override
    def __contains__(self, other: str):
        try:
            self(other)
        except ValueError:
            return False
        return True


@unique
class CaptureMethodEnum(Enum, metaclass=CaptureMethodMeta):
    # Allow TOML to save as a simple string
    @override
    def __repr__(self):
        return self.value
    __str__ = __repr__

    # Allow direct comparison with strings
    @override
    def __eq__(self, other: object):
        return self.value == other.__str__()

    # Restore hashing functionality
    @override
    def __hash__(self):
        return self.value.__hash__()

    NONE = ""
    BITBLT = "BITBLT"
    WINDOWS_GRAPHICS_CAPTURE = "WINDOWS_GRAPHICS_CAPTURE"
    PRINTWINDOW_RENDERFULLCONTENT = "PRINTWINDOW_RENDERFULLCONTENT"
    DESKTOP_DUPLICATION = "DESKTOP_DUPLICATION"
    VIDEO_CAPTURE_DEVICE = "VIDEO_CAPTURE_DEVICE"


class CaptureMethodDict(OrderedDict[CaptureMethodEnum, type[CaptureMethodBase]]):
    def get_index(self, capture_method: str | CaptureMethodEnum):
        """Returns 0 if the capture_method is invalid or unsupported."""
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

    if TYPE_CHECKING:
        @override
        def __getitem__(  # pyright: ignore[reportIncompatibleMethodOverride] # Disallow unsafe get
            self,
            __key: Never,
        ) -> NoReturn: ...

    @override
    def get(self, key: CaptureMethodEnum, __default: object = None):
        """
        Returns the `CaptureMethodBase` subclass for `CaptureMethodEnum` if `CaptureMethodEnum` is available,
        else defaults to the first available `CaptureMethodEnum`.
        Returns `CaptureMethodBase` directly if there's no capture methods.
        """
        if key == CaptureMethodEnum.NONE or len(self) <= 0:
            return CaptureMethodBase
        return super().get(key, first(self.values()))


CAPTURE_METHODS = CaptureMethodDict()
if (  # Windows Graphics Capture requires a minimum Windows Build
    WINDOWS_BUILD_NUMBER >= WGC_MIN_BUILD
    # Our current implementation of Windows Graphics Capture does not ensure we can get an ID3DDevice
    and try_get_direct3d_device()
):
    CAPTURE_METHODS[CaptureMethodEnum.WINDOWS_GRAPHICS_CAPTURE] = WindowsGraphicsCaptureMethod
CAPTURE_METHODS[CaptureMethodEnum.BITBLT] = BitBltCaptureMethod
try:  # Test for laptop cross-GPU Desktop Duplication issue
    import d3dshot
    d3dshot.create(capture_output="numpy")
except (ModuleNotFoundError, COMError):
    pass
else:
    CAPTURE_METHODS[CaptureMethodEnum.DESKTOP_DUPLICATION] = DesktopDuplicationCaptureMethod
CAPTURE_METHODS[CaptureMethodEnum.PRINTWINDOW_RENDERFULLCONTENT] = ForceFullContentRenderingCaptureMethod
CAPTURE_METHODS[CaptureMethodEnum.VIDEO_CAPTURE_DEVICE] = VideoCaptureDeviceCaptureMethod


def change_capture_method(selected_capture_method: CaptureMethodEnum, autosplit: AutoSplit):
    autosplit.capture_method.close(autosplit)
    autosplit.capture_method = CAPTURE_METHODS.get(selected_capture_method)(autosplit)
    if selected_capture_method == CaptureMethodEnum.VIDEO_CAPTURE_DEVICE:
        autosplit.select_region_button.setDisabled(True)
        autosplit.select_window_button.setDisabled(True)
    else:
        autosplit.select_region_button.setDisabled(False)
        autosplit.select_window_button.setDisabled(False)


@dataclass
class CameraInfo:
    device_id: int
    name: str
    occupied: bool
    backend: str
    resolution: tuple[int, int]


def get_input_devices():
    """https://github.com/andreaschiavinato/python_grabber/pull/24 ."""
    return cast(list[str], FilterGraph().get_input_devices())


def get_input_device_resolution(index: int):
    filter_graph = FilterGraph()
    try:
        filter_graph.add_video_input_device(index)
    # This can happen with virtual cameras throwing errors.
    # For example since OBS 29.1 updated FFMPEG breaking VirtualCam 3.0
    # https://github.com/Toufool/AutoSplit/issues/238
    except COMError:
        return None
    resolution = filter_graph.get_input_device().get_current_format()
    filter_graph.remove_filters()
    return resolution


async def get_all_video_capture_devices() -> list[CameraInfo]:
    named_video_inputs = get_input_devices()

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

        resolution = get_input_device_resolution(index)
        return CameraInfo(index, device_name, False, backend, resolution) \
            if resolution is not None \
            else None

    # Note: Return type required https://github.com/python/typeshed/issues/2652
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
