from __future__ import annotations

from collections import OrderedDict
from enum import Enum, EnumMeta, unique
from typing import TYPE_CHECKING, NoReturn, TypedDict, cast

from _ctypes import COMError
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
