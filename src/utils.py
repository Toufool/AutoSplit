import asyncio
import os
import sys
from collections.abc import Callable
from platform import version
from typing import Any, Optional, Union

import cv2
from typing_extensions import TypeGuard


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


def fire_and_forget(func: Callable[..., None]):
    def wrapped(*args: Any, **kwargs: Any):
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
AUTOSPLIT_VERSION = "2.0.0-alpha.4"
START_AUTO_SPLITTER_TEXT = "Start Auto Splitter"
