from __future__ import annotations

import asyncio
import os
import sys
from collections import OrderedDict
from dataclasses import dataclass
from enum import Enum, EnumMeta, unique
from typing import TYPE_CHECKING, TypedDict, cast

from capture_method.CaptureMethodBase import CaptureMethodBase
from capture_method.VideoCaptureDeviceCaptureMethod import VideoCaptureDeviceCaptureMethod
from utils import WGC_MIN_BUILD, WINDOWS_BUILD_NUMBER, first, try_get_direct3d_device

if sys.platform == "win32":
    from _ctypes import COMError  # pylint: disable=import-private-name
    from pygrabber.dshow_graph import FilterGraph

    from capture_method.BitBltCaptureMethod import BitBltCaptureMethod
    from capture_method.DesktopDuplicationCaptureMethod import DesktopDuplicationCaptureMethod
    from capture_method.ForceFullContentRenderingCaptureMethod import ForceFullContentRenderingCaptureMethod
    from capture_method.WindowsGraphicsCaptureMethod import WindowsGraphicsCaptureMethod
if sys.platform == "linux":
    import pyscreeze
    from PIL import features

    from capture_method.ScrotCaptureMethod import ScrotCaptureMethod
    from capture_method.XDisplayCaptureMethod import XDisplayCaptureMethod


if TYPE_CHECKING:
    from AutoSplit import AutoSplit


class Region(TypedDict):
    x: int
    y: int
    width: int
    height: int


class CaptureMethodMeta(EnumMeta):
    # Allow checking if simple string is enum
    def __contains__(self, other: str):
        try:
            self(other)
        except ValueError:
            return False
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
    SCROT = "SCROT"
    XDISPLAY = "XDISPLAY"
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
        __getitem__ = None  # pyright: ignore[reportGeneralTypeIssues] # Disallow unsafe get

    def get(self, __key: CaptureMethodEnum):
        """
        Returns the `CaptureMethodBase` subclass for `CaptureMethodEnum` if `CaptureMethodEnum` is available,
        else defaults to the first available `CaptureMethodEnum`.
        Returns `CaptureMethodBase` (default) directly if there's no capture methods.
        """
        if __key == CaptureMethodEnum.NONE or len(self) <= 0:
            return CaptureMethodBase
        return super().get(__key, first(self.values()))


CAPTURE_METHODS = CaptureMethodDict()
if sys.platform == "win32":
    if (  # Windows Graphics Capture requires a minimum Windows Build
        WINDOWS_BUILD_NUMBER >= WGC_MIN_BUILD
        # Our current implementation of Windows Graphics Capture does not ensure we can get an ID3DDevice
        and try_get_direct3d_device()
    ):
        CAPTURE_METHODS[CaptureMethodEnum.WINDOWS_GRAPHICS_CAPTURE] = WindowsGraphicsCaptureMethod
    CAPTURE_METHODS[CaptureMethodEnum.BITBLT] = BitBltCaptureMethod
    try:
        import d3dshot
        d3dshot.create(capture_output="numpy")
    except (ModuleNotFoundError, COMError):
        pass
    else:
        CAPTURE_METHODS[CaptureMethodEnum.DESKTOP_DUPLICATION] = DesktopDuplicationCaptureMethod
    CAPTURE_METHODS[CaptureMethodEnum.PRINTWINDOW_RENDERFULLCONTENT] = ForceFullContentRenderingCaptureMethod
elif sys.platform == "linux":
    if features.check_feature(feature="xcb"):
        CAPTURE_METHODS[CaptureMethodEnum.XDISPLAY] = XDisplayCaptureMethod
    try:
        pyscreeze.screenshot()
    except NotImplementedError:
        pass
    else:
        # TODO: Investigate solution for Slow Scrot:
        # https://github.com/asweigart/pyscreeze/issues/68
        CAPTURE_METHODS[CaptureMethodEnum.SCROT] = ScrotCaptureMethod
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
class CameraInfo():
    device_id: int
    name: str
    occupied: bool
    backend: str
    resolution: tuple[int, int] | None


def get_input_devices():
    if sys.platform == "win32":
        # https://github.com/andreaschiavinato/python_grabber/pull/24
        return cast(list[str], FilterGraph().get_input_devices())

    cameras: list[str] = []
    if sys.platform == "linux":
        try:
            for index in range(len(os.listdir("/sys/class/video4linux"))):
                with open(f"/sys/class/video4linux/video{index}/name", encoding="utf-8") as file:
                    cameras.append(file.readline()[:-2])
        except FileNotFoundError:
            pass
    return cameras


def get_input_device_resolution(index: int):
    if sys.platform == "win32":
        filter_graph = FilterGraph()
        filter_graph.add_video_input_device(index)
        resolution = filter_graph.get_input_device().get_current_format()
        filter_graph.remove_filters()
        return resolution
    return None


async def get_all_video_capture_devices():
    named_video_inputs = get_input_devices()

    async def get_camera_info(index: int, device_name: str):
        backend = ""
        # Probing freezes some devices (like GV-USB2 and AverMedia) if already in use
        # #169
        # FIXME: Maybe offer the option to the user to obtain more info about their devies?
        #        Off by default. With a tooltip to explain the risk.
        # video_capture=cv2.VideoCapture(index)
        # video_capture.setExceptionMode(True)
        # try:
        #     # https://docs.opencv.org/3.4/d4/d15/group__videoio__flags__base.html#ga023786be1ee68a9105bf2e48c700294d
        #     backend=video_capture.getBackendName()  # STS_ASSERT
        #     video_capture.grab()  # STS_ERROR
        # except cv2.error as error:
        #     return CameraInfo(index, device_name, True, backend) \
        #         if error.code in (cv2.Error.STS_ERROR, cv2.Error.STS_ASSERT) \
        #         else None
        # finally:
        #     video_capture.release()

        return CameraInfo(index, device_name, False, backend, get_input_device_resolution(index))

    # https://github.com/python/typeshed/issues/2652
    future: asyncio.Future[list[CameraInfo | None]] = asyncio.gather(
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
