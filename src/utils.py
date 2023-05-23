from __future__ import annotations

import asyncio
import ctypes
import ctypes.wintypes
import os
import sys
from collections.abc import Callable, Iterable
from enum import IntEnum
from platform import version
from threading import Thread
from typing import TYPE_CHECKING, Any, TypeVar, cast

import cv2
import win32ui
from typing_extensions import TypeGuard
from win32 import win32gui
from winsdk.windows.ai.machinelearning import LearningModelDevice, LearningModelDeviceKind
from winsdk.windows.media.capture import MediaCapture

from gen.build_vars import AUTOSPLIT_BUILD_NUMBER, AUTOSPLIT_GITHUB_REPOSITORY

if TYPE_CHECKING:
    # Source does not exist, keep this under TYPE_CHECKING
    from _win32typing import PyCDC  # pyright: ignore[reportMissingModuleSource]

DWMWA_EXTENDED_FRAME_BOUNDS = 9
MAXBYTE = 255
RGB_CHANNEL_COUNT = 3
"""How many channels in an RGB image"""
RGBA_CHANNEL_COUNT = 4
"""How many channels in an RGB image"""


class ImageShape(IntEnum):
    X = 0
    Y = 1
    Channels = 2


class ColorChannel(IntEnum):
    Red = 0
    Green = 1
    Blue = 2
    Alpha = 3


def decimal(value: int | float):
    # Using ljust instead of :2f because of python float rounding errors
    return f"{int(value * 100) / 100}".ljust(4, "0")


def is_digit(value: str | int | None):
    """Checks if `value` is a single-digit string from 0-9."""
    if value is None:
        return False
    try:
        return 0 <= int(value) <= 9  # noqa: PLR2004
    except (ValueError, TypeError):
        return False


def is_valid_image(image: cv2.Mat | None) -> TypeGuard[cv2.Mat]:
    return image is not None and bool(image.size)


def is_valid_hwnd(hwnd: int):
    """Validate the hwnd points to a valid window and not the desktop or whatever window obtained with `""`."""
    if not hwnd:
        return False
    if sys.platform == "win32":
        # TODO: Fix stubs, IsWindow should return a boolean
        return bool(win32gui.IsWindow(hwnd) and win32gui.GetWindowText(hwnd))
    return True


T = TypeVar("T")


def first(iterable: Iterable[T]) -> T:
    """@return: The first element of a collection. Dictionaries will return the first key."""
    return next(iter(iterable))


def try_delete_dc(dc: PyCDC):
    try:
        dc.DeleteDC()
    except win32ui.error:
        pass


def get_window_bounds(hwnd: int) -> tuple[int, int, int, int]:
    extended_frame_bounds = ctypes.wintypes.RECT()
    ctypes.windll.dwmapi.DwmGetWindowAttribute(
        hwnd,
        DWMWA_EXTENDED_FRAME_BOUNDS,
        ctypes.byref(extended_frame_bounds),
        ctypes.sizeof(extended_frame_bounds),
    )

    window_rect = win32gui.GetWindowRect(hwnd)
    window_left_bounds = cast(int, extended_frame_bounds.left) - window_rect[0]
    window_top_bounds = cast(int, extended_frame_bounds.top) - window_rect[1]
    window_width = cast(int, extended_frame_bounds.right) - cast(int, extended_frame_bounds.left)
    window_height = cast(int, extended_frame_bounds.bottom) - cast(int, extended_frame_bounds.top)
    return window_left_bounds, window_top_bounds, window_width, window_height


def open_file(file_path: str | bytes | os.PathLike[str] | os.PathLike[bytes]):
    os.startfile(file_path)  # noqa: S606


def get_or_create_eventloop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return asyncio.get_event_loop()


def get_direct3d_device():
    # Note: Must create in the same thread (can't use a global) otherwise when ran from LiveSplit it will raise:
    # OSError: The application called an interface that was marshalled for a different thread
    media_capture = MediaCapture()

    async def init_mediacapture():
        await (media_capture.initialize_async() or asyncio.sleep(0))
    asyncio.run(init_mediacapture())
    direct_3d_device = media_capture.media_capture_settings and \
        media_capture.media_capture_settings.direct3_d11_device
    if not direct_3d_device:
        try:
            # May be problematic? https://github.com/pywinrt/python-winsdk/issues/11#issuecomment-1315345318
            direct_3d_device = LearningModelDevice(LearningModelDeviceKind.DIRECT_X_HIGH_PERFORMANCE).direct3_d11_device
        # TODO: Unknown potential error, I don't have an older Win10 machine to test.
        except BaseException:  # noqa: S110,BLE001
            pass
    if not direct_3d_device:
        raise OSError("Unable to initialize a Direct3D Device.")
    return direct_3d_device


def try_get_direct3d_device():
    try:
        return get_direct3d_device()
    except OSError:
        return None


def fire_and_forget(func: Callable[..., Any]):
    """
    Runs synchronous function asynchronously without waiting for a response.

    Uses threads on Windows because `RuntimeError: There is no current event loop in thread 'MainThread'.`

    Uses asyncio on Linux because of a `Segmentation fault (core dumped)`
    """
    def wrapped(*args: Any, **kwargs: Any):
        if sys.platform == "win32":
            thread = Thread(target=func, args=args, kwargs=kwargs)
            thread.start()
            return thread
        return get_or_create_eventloop().run_in_executor(None, func, *args, *kwargs)

    return wrapped


def getTopWindowAt(x: int, y: int):  # noqa: N802
    # Immitating PyWinCTL's function
    class Win32Window():
        def __init__(self, hwnd: int) -> None:
            self._hWnd = hwnd

        def getHandle(self):  # noqa: N802
            return self._hWnd

        @property
        def title(self):
            return win32gui.GetWindowText(self._hWnd)
    hwnd = win32gui.WindowFromPoint((x, y))

    # Want to pull the parent window from the window handle
    # By using GetAncestor we are able to get the parent window instead of the owner window.
    while win32gui.IsChild(win32gui.GetParent(hwnd), hwnd):
        hwnd = ctypes.windll.user32.GetAncestor(hwnd, 2)
    return Win32Window(hwnd) if hwnd else None


# Environment specifics
WINDOWS_BUILD_NUMBER = int(version().split(".")[-1]) if sys.platform == "win32" else -1
FIRST_WIN_11_BUILD = 22000
"""AutoSplit Version number"""
FROZEN = hasattr(sys, "frozen")
"""Running from build made by PyInstaller"""
auto_split_directory = os.path.dirname(sys.executable if FROZEN else os.path.abspath(__file__))
"""The directory of either the AutoSplit executable or AutoSplit.py"""

# Shared strings
# Check `excludeBuildNumber` during workflow dispatch build generate a clean version number
AUTOSPLIT_VERSION = "2.0.1" + (f"-{AUTOSPLIT_BUILD_NUMBER}" if AUTOSPLIT_BUILD_NUMBER else "")
GITHUB_REPOSITORY = AUTOSPLIT_GITHUB_REPOSITORY
