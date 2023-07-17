from __future__ import annotations

import asyncio
import ctypes
import ctypes.wintypes
import os
import sys
from collections.abc import Callable, Generator, Iterable
from enum import Enum
from platform import version
from threading import Thread
from typing import TYPE_CHECKING, Any, Final, TypeVar, cast

import win32ui
from typing_extensions import TypeGuard
from win32 import win32gui
from winsdk.windows.ai.machinelearning import LearningModelDevice, LearningModelDeviceKind
from winsdk.windows.media.capture import MediaCapture

from gen.build_vars import AUTOSPLIT_BUILD_NUMBER, AUTOSPLIT_GITHUB_REPOSITORY

if TYPE_CHECKING:
    # Source does not exist, keep this under TYPE_CHECKING
    from _win32typing import PyCDC  # pyright: ignore[reportMissingModuleSource]
    from cv2.typing import MatLike  # pyright: ignore[reportMissingModuleSource]

_T = TypeVar("_T")


DWMWA_EXTENDED_FRAME_BOUNDS: Final = 9
MAXBYTE: Final = 255
BGR_CHANNEL_COUNT: Final = 3
"""How many channels in an RGB image"""
BGRA_CHANNEL_COUNT: Final = 4
"""How many channels in an RGBA image"""

# TODO: Switch back to IntEnum and remove all `.value` once fixed in mypyc
# https://github.com/mypyc/mypyc/issues/721


class ImageShape(Enum):
    Y = 0
    X = 1
    Channels = 2


class ColorChannel(Enum):
    Blue = 0
    Green = 1
    Red = 2
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


def is_valid_image(image: MatLike | None) -> TypeGuard[MatLike]:
    return image is not None and bool(image.size)


def is_valid_hwnd(hwnd: int) -> bool:
    """Validate the hwnd points to a valid window and not the desktop or whatever window obtained with `""`."""
    if not hwnd:
        return False
    if sys.platform == "win32":
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
    direct_3d_device = media_capture.media_capture_settings and media_capture.media_capture_settings.direct3_d11_device
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

    Uses threads on Windows because ~~`RuntimeError: There is no current event loop in thread 'MainThread'.`~~
    Because maybe asyncio has issues. Unsure. See alpha.5 and https://github.com/Avasam/AutoSplit/issues/36

    Uses asyncio on Linux because of a `Segmentation fault (core dumped)`
    """

    def wrapped(*args: Any, **kwargs: Any):
        if sys.platform == "win32":
            thread = Thread(target=func, args=args, kwargs=kwargs)
            thread.start()
            return thread
        return get_or_create_eventloop().run_in_executor(None, func, *args, *kwargs)

    return wrapped


def flatten(nested_iterable: Iterable[Iterable[_T]]) -> Generator[_T, None, None]:
    return (
        item for flatten
        in nested_iterable
        for item in flatten
    )


def __get_auto_split_directory():
    """
    `Cpython` doesn't populate `__file__` until after the module init routine returns,
    so modules that reference at the toplevel will be busted.
    https://github.com/mypyc/mypyc/issues/700 .
    """
    return os.path.dirname(sys.executable if frozen else os.path.abspath(__file__))


# Environment specifics
WINDOWS_BUILD_NUMBER: Final = int(version().split(".")[-1]) if sys.platform == "win32" else -1
FIRST_WIN_11_BUILD: Final = 22000
"""AutoSplit Version number"""
WGC_MIN_BUILD: Final = 17134
"""https://docs.microsoft.com/en-us/uwp/api/windows.graphics.capture.graphicscapturepicker#applies-to"""
# NOTE: Do NOT mark as Final, "sys.frozen" is set by PyInstaller,
# we don't want mypyc to early bind this to Literal[False]
frozen = hasattr(sys, "frozen")
"""Running from build made by PyInstaller"""
auto_split_directory = __get_auto_split_directory()
"""The directory of either the AutoSplit executable or AutoSplit.py"""

# Shared strings
# Check `excludeBuildNumber` during workflow dispatch build generate a clean version number
AUTOSPLIT_VERSION: Final = "2.1.0" + (f"-{AUTOSPLIT_BUILD_NUMBER}" if AUTOSPLIT_BUILD_NUMBER else "")
GITHUB_REPOSITORY: Final = AUTOSPLIT_GITHUB_REPOSITORY
