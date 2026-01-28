# ruff: noqa: RUF067
from __future__ import annotations

import os
import sys
from collections import OrderedDict
from dataclasses import dataclass
from enum import EnumMeta, StrEnum, auto, unique
from itertools import starmap
from typing import TYPE_CHECKING, Never, TypedDict, cast, override

from capture_method.CaptureMethodBase import CaptureMethodBase
from capture_method.VideoCaptureDeviceCaptureMethod import VideoCaptureDeviceCaptureMethod
from utils import WGC_MIN_BUILD, WINDOWS_BUILD_NUMBER, first, get_input_device_resolution

if sys.platform == "win32":
    from _ctypes import COMError  # noqa: PLC2701 # comtypes is untyped

    from capture_method.BitBltCaptureMethod import BitBltCaptureMethod
    from capture_method.DesktopDuplicationCaptureMethod import DesktopDuplicationCaptureMethod
    from capture_method.ForceFullContentRenderingCaptureMethod import (
        ForceFullContentRenderingCaptureMethod,
    )
    from capture_method.WindowsGraphicsCaptureMethod import WindowsGraphicsCaptureMethod

if sys.platform == "linux":
    import pyscreeze
    from PIL import UnidentifiedImageError, features

    from capture_method.ScrotCaptureMethod import ScrotCaptureMethod
    from capture_method.XcbCaptureMethod import XcbCaptureMethod


if TYPE_CHECKING:
    from AutoSplit import AutoSplit


class Region(TypedDict):
    x: int
    y: int
    width: int
    height: int


class ContainerEnumMeta(EnumMeta):
    # Allow checking if simple string is enum
    @override
    def __contains__(cls, value: object):
        try:
            cls(value)
        except ValueError:
            return False
        return True


@unique
class CaptureMethodEnum(StrEnum, metaclass=ContainerEnumMeta):
    # Capitalize the string value from auto()
    @override
    @staticmethod
    def _generate_next_value_(
        name: str,
        start: int,
        count: int,
        last_values: list[str],
    ) -> str:
        return name

    NONE = ""
    BITBLT = auto()
    WINDOWS_GRAPHICS_CAPTURE = auto()
    PRINTWINDOW_RENDERFULLCONTENT = auto()
    DESKTOP_DUPLICATION = auto()
    SCROT = auto()
    XCB = auto()
    VIDEO_CAPTURE_DEVICE = auto()


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

    # Disallow unsafe get w/o breaking it at runtime
    @override
    def __getitem__(  # type: ignore[override] # pyright: ignore[reportIncompatibleMethodOverride]
        self, key: Never, /
    ) -> type[CaptureMethodBase]:
        return super().__getitem__(key)

    @override
    def get(self, key: CaptureMethodEnum, default: object = None, /):
        """
        Returns the `CaptureMethodBase` subclass for `CaptureMethodEnum`
        if `CaptureMethodEnum` is available,
        else defaults to the first available `CaptureMethodEnum`.
        Returns `CaptureMethodBase` directly if there's no capture methods.
        """
        if key == CaptureMethodEnum.NONE or len(self) <= 0:
            return CaptureMethodBase
        return super().get(key, first(self.values()))


CAPTURE_METHODS = CaptureMethodDict()
if sys.platform == "win32":
    # Windows Graphics Capture requires a minimum Windows Build
    if WINDOWS_BUILD_NUMBER >= WGC_MIN_BUILD:
        CAPTURE_METHODS[CaptureMethodEnum.WINDOWS_GRAPHICS_CAPTURE] = WindowsGraphicsCaptureMethod
    CAPTURE_METHODS[CaptureMethodEnum.BITBLT] = BitBltCaptureMethod
    try:  # Test for laptop cross-GPU Desktop Duplication issue
        import d3dshot

        d3dshot.create(capture_output="numpy")
    except (ModuleNotFoundError, COMError):
        pass
    else:
        CAPTURE_METHODS[CaptureMethodEnum.DESKTOP_DUPLICATION] = DesktopDuplicationCaptureMethod
    CAPTURE_METHODS[CaptureMethodEnum.PRINTWINDOW_RENDERFULLCONTENT] = (
        ForceFullContentRenderingCaptureMethod
    )
elif sys.platform == "linux":
    if features.check_feature(feature="xcb"):
        CAPTURE_METHODS[CaptureMethodEnum.XCB] = XcbCaptureMethod
    try:
        pyscreeze.screenshot()
    except (UnidentifiedImageError, pyscreeze.PyScreezeException):
        # TODO: Should we show a specific warning for, or document:
        # pyscreeze.PyScreezeException: Your computer uses the Wayland window system. Scrot works on the X11 window system but not Wayland. You must install gnome-screenshot by running `sudo apt install gnome-screenshot` # noqa: E501
        pass
    else:
        # TODO: Investigate solution for Slow Scrot:
        # https://github.com/asweigart/pyscreeze/issues/68
        CAPTURE_METHODS[CaptureMethodEnum.SCROT] = ScrotCaptureMethod
CAPTURE_METHODS[CaptureMethodEnum.VIDEO_CAPTURE_DEVICE] = VideoCaptureDeviceCaptureMethod


def change_capture_method(selected_capture_method: CaptureMethodEnum, autosplit: AutoSplit):
    """
    Seamlessly change the current capture method,
    initialize the new one with transferred subscriptions
    and update UI as needed.
    """
    autosplit.capture_method.close()
    autosplit.capture_method = CAPTURE_METHODS.get(selected_capture_method)(autosplit)

    disable_selection_buttons = selected_capture_method == CaptureMethodEnum.VIDEO_CAPTURE_DEVICE
    autosplit.select_region_button.setDisabled(disable_selection_buttons)
    autosplit.select_window_button.setDisabled(disable_selection_buttons)


@dataclass
class CameraInfo:
    device_id: int
    name: str
    occupied: bool
    backend: str
    resolution: tuple[int, int]


def get_input_devices():
    if sys.platform == "win32":
        try:
            from pygrabber.dshow_graph import FilterGraph  # noqa: PLC0415
        except OSError as exception:
            # wine can choke on D3D Device Enumeration if missing directshow
            # OSError: [WinError -2147312566] Windows Error 0x80029c4a
            # TODO: Check the OS error number and only silence that one
            print(exception)
            print(exception.errno)
            print(exception.winerror)
            return list[str]()
        return FilterGraph().get_input_devices()

    cameras: list[str] = []
    if sys.platform == "linux":
        try:
            for index in range(len(os.listdir("/sys/class/video4linux"))):
                with open(f"/sys/class/video4linux/video{index}/name", encoding="utf-8") as file:
                    cameras.append(file.readline()[:-2])
        except FileNotFoundError:
            pass
    return cameras


def get_all_video_capture_devices():
    named_video_inputs = get_input_devices()

    def get_camera_info(index: int, device_name: str):
        backend = ""
        # Probing freezes some devices (like GV-USB2 and AverMedia) if already in use. See #169
        # FIXME: Maybe offer the option to the user to obtain more info about their devices?
        #        Off by default. With a tooltip to explain the risk.
        # video_capture = cv2.VideoCapture(index)
        # video_capture.setExceptionMode(True)
        # try:
        #     # https://docs.opencv.org/3.4/d4/d15/group__videoio__flags__base.html#ga023786be1ee68a9105bf2e48c700294d
        #     backend = video_capture.getBackendName()  # STS_ASSERT
        #     video_capture.grab()  # STS_ERROR
        # except cv2.error as error:
        #     return (
        #         CameraInfo(index, device_name, True, backend)
        #         if error.code in (cv2.Error.STS_ERROR, cv2.Error.STS_ASSERT)
        #         else None
        #     )
        # finally:
        #     video_capture.release()

        resolution = get_input_device_resolution(index)
        return (
            CameraInfo(index, device_name, False, backend, resolution)
            if resolution is not None
            else None
        )

    return list(filter(None, starmap(get_camera_info, enumerate(named_video_inputs))))
