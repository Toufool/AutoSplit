from __future__ import annotations

import asyncio
import ctypes
import ctypes.wintypes
import os
import sys
from collections.abc import Callable, Iterable
from platform import version
from typing import TYPE_CHECKING, Any, TypeVar, cast

import cv2
from PyQt6 import QtCore
from PyQt6.QtWidgets import QApplication, QMainWindow
from win32 import win32gui

from gen.build_vars import AUTOSPLIT_BUILD_NUMBER, AUTOSPLIT_GITHUB_REPOSITORY

if TYPE_CHECKING:
    from typing_extensions import ParamSpec, TypeGuard

    from AutoSplit import AutoSplit
    P = ParamSpec("P")

DWMWA_EXTENDED_FRAME_BOUNDS = 9


def decimal(value: int | float):
    return f"{int(value * 100) / 100:.2f}"


def is_digit(value: str | int | None):
    """
    Checks if `value` is a single-digit string from 0-9
    """
    if value is None:
        return False
    try:
        return 0 <= int(value) <= 9
    except (ValueError, TypeError):
        return False


def is_valid_image(image: cv2.Mat | None) -> TypeGuard[cv2.Mat]:
    return image is not None and bool(image.size)


def is_valid_hwnd(hwnd: int):
    """Validate the hwnd points to a valid window and not the desktop or whatever window obtained with `\"\"`"""
    return bool(hwnd and win32gui.IsWindow(hwnd) and win32gui.GetWindowText(hwnd))


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


def find_autosplit_main_window() -> AutoSplit:
    # TODO: Make singleton
    # Global function to find the (open) QMainWindow in application
    for widget in QApplication.topLevelWidgets():
        if isinstance(widget, QMainWindow):
            return widget  # pyright: ignore [reportGeneralTypeIssues]
    raise ModuleNotFoundError()


def get_or_create_eventloop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return asyncio.get_event_loop()


def fire_and_forget(func: Callable[..., Any]):
    """
    Runs synchronous function asynchronously without waiting for a response

    Uses threads on Windows because `RuntimeError: There is no current event loop in thread 'MainThread'.`

    Uses asyncio on Linux because of a `Segmentation fault (core dumped)`
    """
    def wrapped(*args: Any, **kwargs: Any):
        if sys.platform == "win32":
            autosplit = find_autosplit_main_window()
            thread = QtCore.QThread()
            worker = QtCore.QObject()
            autosplit.threads[id(thread)] = (thread, worker)
            worker.moveToThread(thread)

            def to_run():
                func(*args, **kwargs)
                thread.quit()
                worker.deleteLater()
            thread.started.connect(to_run)
            thread.finished.connect(thread.deleteLater)
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
"""The directory of either the AutoSplit executable or AutoSplit.py"""

# Shared strings
# Set AUTOSPLIT_BUILD_NUMBER to an empty string to generate a clean version number
# AUTOSPLIT_BUILD_NUMBER = ""  # pyright: ignore[reportConstantRedefinition]  # noqa: F811
AUTOSPLIT_VERSION = "2.0.0-alpha.5" + (f"-{AUTOSPLIT_BUILD_NUMBER}" if AUTOSPLIT_BUILD_NUMBER else "")
START_AUTO_SPLITTER_TEXT = "Start Auto Splitter"
GITHUB_REPOSITORY = AUTOSPLIT_GITHUB_REPOSITORY
