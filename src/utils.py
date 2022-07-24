from __future__ import annotations

import asyncio
import ctypes
import ctypes.wintypes
import os
import sys
from collections.abc import Callable, Iterable
from platform import version
from threading import Thread
from typing import TYPE_CHECKING, Any, Optional, TypeVar, Union, cast

import cv2
from win32 import win32gui

from gen.build_number import AUTOSPLIT_BUILD_NUMBER

if TYPE_CHECKING:
    from typing_extensions import TypeGuard

DWMWA_EXTENDED_FRAME_BOUNDS = 9


def decimal(value: Union[int, float]):
    return f"{int(value * 100) / 100:.2f}"


def is_digit(value: Optional[Union[str, int]]):
    """
    Checks if `value` is a single-digit string from 0-9
    """
    if value is None:
        return False
    try:
        return 0 <= int(value) <= 9
    except (ValueError, TypeError):
        return False


def is_valid_image(image: Optional[cv2.Mat]) -> TypeGuard[cv2.Mat]:
    return image is not None and bool(image.size)


def is_valid_hwnd(hwnd: int):
    """Validate the hwnd points to a valid window and not the desktop or whatever window obtained with `\"\"`"""
    if not hwnd:
        return False
    if sys.platform == "win32":
        return bool(win32gui.IsWindow(hwnd) and win32gui.GetWindowText(hwnd))
    return True


T = TypeVar("T")


def first(iterable: Iterable[T]) -> T:
    """@return: The first element of a collection. Dictionaries will return the first key"""
    return next(iter(iterable))


def get_window_bounds(hwnd: int) -> tuple[int, int, int, int]:
    extended_frame_bounds = ctypes.wintypes.RECT()
    ctypes.windll.dwmapi.DwmGetWindowAttribute(
        hwnd,
        DWMWA_EXTENDED_FRAME_BOUNDS,
        ctypes.byref(extended_frame_bounds),
        ctypes.sizeof(extended_frame_bounds))

    window_rect = win32gui.GetWindowRect(hwnd)
    window_left_bounds = cast(int, extended_frame_bounds.left) - window_rect[0]
    window_top_bounds = cast(int, extended_frame_bounds.top) - window_rect[1]
    window_width = cast(int, extended_frame_bounds.right) - cast(int, extended_frame_bounds.left)
    window_height = cast(int, extended_frame_bounds.bottom) - cast(int, extended_frame_bounds.top)
    return window_left_bounds, window_top_bounds, window_width, window_height


def fire_and_forget(func: Callable[..., Any]):
    """
    Runs synchronous function asynchronously without waiting for a response

    Uses threads on Windows because `RuntimeError: There is no current event loop in thread 'MainThread'.`

    Uses asyncio on Linux because of a `Segmentation fault (core dumped)`
    """
    def wrapped(*args: Any, **kwargs: Any):
        if sys.platform == "win32":
            thread = Thread(target=func, args=args, kwargs=kwargs)
            thread.start()
            return thread
        return asyncio.get_event_loop().run_in_executor(None, func, *args, *kwargs)

    return wrapped


# Environment specifics
WINDOWS_BUILD_NUMBER = int(version().split(".")[2])
FIRST_WIN_11_BUILD = 22000
"""AutoSplit Version number"""
FROZEN = hasattr(sys, "frozen")
"""Running from build made by PyInstaller"""
auto_split_directory = os.path.dirname(sys.executable if FROZEN else os.path.abspath(__file__))
"""The directory of either AutoSplit.exe or AutoSplit.py"""

# Shared strings
# DIRTY_VERSION_EXTENSION = ""
DIRTY_VERSION_EXTENSION = "-" + AUTOSPLIT_BUILD_NUMBER
"""Set DIRTY_VERSION_EXTENSION to an empty string to generate a clean version number"""
AUTOSPLIT_VERSION = "2.0.0-alpha.4" + DIRTY_VERSION_EXTENSION
START_AUTO_SPLITTER_TEXT = "Start Auto Splitter"
