import asyncio
import os
import shutil
import subprocess  # noqa: S404
import sys
from collections.abc import Callable, Iterable, Sequence
from enum import IntEnum
from functools import partial
from itertools import chain
from platform import version
from threading import Thread
from typing import TYPE_CHECKING, Any, TypedDict, TypeGuard, TypeVar

import cv2
import numpy as np
from cv2.typing import MatLike

from gen.build_vars import AUTOSPLIT_BUILD_NUMBER, AUTOSPLIT_GITHUB_REPOSITORY

if sys.platform == "win32":
    import ctypes
    import ctypes.wintypes
    from _ctypes import COMError  # noqa: PLC2701 # comtypes is untyped

    import win32gui
    import win32ui
    from pygrabber.dshow_graph import FilterGraph

    STARTUPINFO = subprocess.STARTUPINFO
else:
    STARTUPINFO = None

if sys.platform == "linux":
    import fcntl

    from pyscreeze import RUNNING_WAYLAND as RUNNING_WAYLAND  # noqa: PLC0414

else:
    RUNNING_WAYLAND = False


if TYPE_CHECKING:
    # Source does not exist, keep this under TYPE_CHECKING
    from _win32typing import PyCDC  # pyright: ignore[reportMissingModuleSource]

T = TypeVar("T")


def find_tesseract_path():
    search_path = os.environ.get("PATH", os.defpath)
    if sys.platform == "win32":
        search_path += r";C:\Program Files\Tesseract-OCR;C:\Program Files (x86)\Tesseract-OCR"
    return shutil.which(TESSERACT_EXE, path=search_path)


TESSERACT_EXE = "tesseract"
TESSERACT_PATH = find_tesseract_path()
"""The path to execute tesseract. `None` if it can't be found."""
TESSERACT_CMD = (TESSERACT_PATH or TESSERACT_EXE, "-", "-", "--oem", "1", "--psm", "6")

DWMWA_EXTENDED_FRAME_BOUNDS = 9
MAXBYTE = 255
ONE_SECOND = 1000
"""1000 milliseconds in 1 second"""
BGR_CHANNEL_COUNT = 3
"""How many channels in a BGR image"""
BGRA_CHANNEL_COUNT = 4
"""How many channels in a BGRA image"""


class ImageShape(IntEnum):
    Y = 0
    X = 1
    Channels = 2


class ColorChannel(IntEnum):
    Blue = 0
    Green = 1
    Red = 2
    Alpha = 3


class SubprocessKWArgs(TypedDict):
    stdin: int
    stdout: int
    stderr: int
    startupinfo: "STARTUPINFO | None"
    env: os._Environ[str] | None  # pyright: ignore[reportPrivateUsage]


def decimal(value: float):
    # Using ljust instead of :2f because of python float rounding errors
    return f"{int(value * 100) / 100}".ljust(4, "0")


def is_digit(value: str | int | None):
    """Checks if `value` is a single-digit string from 0-9."""
    if value is None:
        return False
    try:
        return 0 <= int(value) <= 9
    except (ValueError, TypeError):
        return False


def is_valid_image(image: MatLike | None) -> TypeGuard[MatLike]:
    return image is not None and bool(image.size)


def is_valid_hwnd(hwnd: int):
    """
    Validate the hwnd points to a valid window
    and not the desktop or whatever window obtained with `""`.
    """
    if not hwnd:
        return False
    if sys.platform == "win32":
        return bool(win32gui.IsWindow(hwnd) and win32gui.GetWindowText(hwnd))
    return True


def first(iterable: Iterable[T]) -> T:
    """@return: The first element of a collection. Dictionaries will return the first key."""
    return next(iter(iterable))


def try_delete_dc(dc: "PyCDC"):
    if sys.platform != "win32":
        raise OSError
    try:
        dc.DeleteDC()
    except win32ui.error:
        pass


def get_window_bounds(hwnd: int) -> tuple[int, int, int, int]:
    if sys.platform != "win32":
        raise OSError

    extended_frame_bounds = ctypes.wintypes.RECT()
    ctypes.windll.dwmapi.DwmGetWindowAttribute(
        hwnd,
        DWMWA_EXTENDED_FRAME_BOUNDS,
        ctypes.byref(extended_frame_bounds),
        ctypes.sizeof(extended_frame_bounds),
    )

    window_rect = win32gui.GetWindowRect(hwnd)
    window_left_bounds = extended_frame_bounds.left - window_rect[0]
    window_top_bounds = extended_frame_bounds.top - window_rect[1]
    window_width = extended_frame_bounds.right - extended_frame_bounds.left
    window_height = extended_frame_bounds.bottom - extended_frame_bounds.top
    return window_left_bounds, window_top_bounds, window_width, window_height


# Note: maybe reorganize capture_method module to have
# different helper modules and a methods submodule
def get_input_device_resolution(index: int) -> tuple[int, int] | None:
    if sys.platform != "win32":
        return (0, 0)
    filter_graph = FilterGraph()
    try:
        filter_graph.add_video_input_device(index)
    # This can happen with virtual cameras throwing errors.
    # For example since OBS 29.1 updated FFMPEG breaking VirtualCam 3.0
    # https://github.com/Toufool/AutoSplit/issues/238
    except COMError:
        return None

    try:
        resolution = filter_graph.get_input_device().get_current_format()
    # For unknown reasons, some devices can raise "ValueError: NULL pointer access".
    # For instance, Oh_DeeR's AVerMedia HD Capture C985 Bus 12
    except ValueError:
        return None
    finally:
        filter_graph.remove_filters()
    return resolution


def open_file(file_path: str | bytes | os.PathLike[str] | os.PathLike[bytes]):
    if sys.platform == "win32":
        os.startfile(file_path)  # noqa: S606
    else:
        opener = "xdg-open" if sys.platform == "linux" else "open"
        subprocess.call([opener, file_path])  # noqa: S603


def get_or_create_eventloop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return asyncio.get_event_loop()


def try_input_device_access():
    """Same as `make_uinput` in `keyboard/_nixcommon.py`."""
    if sys.platform != "linux":
        return False
    try:
        UI_SET_EVBIT = 0x40045564  # noqa: N806
        with open("/dev/uinput", "wb") as uinput:
            fcntl.ioctl(uinput, UI_SET_EVBIT)
    except OSError:
        return False
    return True


def fire_and_forget(func: Callable[..., Any]):
    """
    Runs synchronous function asynchronously without waiting for a response.

    Uses threads on Windows because
    ~~`RuntimeError: There is no current event loop in thread 'MainThread'`~~
    maybe asyncio has issues. Unsure. See alpha.5 and https://github.com/Avasam/AutoSplit/issues/36

    Uses asyncio on Linux because of a `Segmentation fault (core dumped)`
    """

    def wrapped(*args: Any, **kwargs: Any):
        if sys.platform == "win32":
            thread = Thread(target=func, args=args, kwargs=kwargs)
            thread.start()
            return thread
        return get_or_create_eventloop().run_in_executor(None, partial(func, *args, **kwargs))

    return wrapped


def flatten(nested_iterable: Iterable[Iterable[T]]) -> chain[T]:
    return chain.from_iterable(nested_iterable)


def imread(filename: str, flags: int = cv2.IMREAD_COLOR):
    return cv2.imdecode(np.fromfile(filename, dtype=np.uint8), flags)


def imwrite(filename: str, img: MatLike, params: Sequence[int] = ()):
    success, encoded_img = cv2.imencode(os.path.splitext(filename)[1], img, params)
    if not success:
        raise OSError(f"cv2 could not write to path {filename}")
    encoded_img.tofile(filename)


def subprocess_kwargs():
    """
    Create a set of arguments which make a ``subprocess.Popen`` (and
    variants) call work with or without Pyinstaller, ``--noconsole`` or
    not, on Windows and Linux.

    Typical use:
    ```python
    subprocess.call(["program_to_run", "arg_1"], **subprocess_args())
    ```
    ---
    Originally found in https://github.com/madmaze/pytesseract/blob/master/pytesseract/pytesseract.py
    Recipe from https://github.com/pyinstaller/pyinstaller/wiki/Recipe-subprocess
    which itself is taken from https://github.com/bjones1/enki/blob/master/enki/lib/get_console_output.py
    """
    # The following is true only on Windows.
    if sys.platform == "win32":
        # On Windows, subprocess calls will pop up a command window by default when run from
        # Pyinstaller with the ``--noconsole`` option. Avoid this distraction.
        startupinfo = STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        # https://github.com/madmaze/pytesseract/blob/88839f03590578a10e806a5244704437c9d477da/pytesseract/pytesseract.py#L236
        startupinfo.wShowWindow = subprocess.SW_HIDE
        # Windows doesn't search the path by default. Pass it an environment so it will.
        env = os.environ
    else:
        startupinfo = None
        env = None
    # On Windows, running this from the binary produced by Pyinstaller
    # with the ``--noconsole`` option requires redirecting everything
    # (stdin, stdout, stderr) to avoid an OSError exception
    # "[Error 6] the handle is invalid."
    return SubprocessKWArgs(
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        startupinfo=startupinfo,
        env=env,
    )


def run_tesseract(png: bytes):
    """
    Executes the tesseract CLI and pipes a PNG encoded image to it.
    @param png: PNG encoded image as byte array
    @return: The recognized output string from tesseract.
    """
    return (
        subprocess.Popen(  # noqa: S603 # Only using known literal strings or shutil.which result
            TESSERACT_CMD, **subprocess_kwargs()
        )
        .communicate(input=png)[0]
        .decode()
    )


def list_processes():
    if sys.platform == "win32":
        return [
            # The first row is the process name
            line.split()[0]
            for line in subprocess.check_output(
                "C:/Windows/System32/tasklist.exe", text=True
            ).splitlines()[3:]  # Skip the table header lines
            if line
        ]

    return subprocess.check_output(
        ("ps", "-eo", "comm"),
        text=True,
    ).splitlines()[1:]  # Skip the header line


# Environment specifics
WINDOWS_BUILD_NUMBER = int(version().split(".")[-1]) if sys.platform == "win32" else -1
FIRST_WIN_11_BUILD = 22000
WGC_MIN_BUILD = 17134
"""https://docs.microsoft.com/en-us/uwp/api/windows.graphics.capture.graphicscapturepicker#applies-to"""
FROZEN = hasattr(sys, "frozen")
"""Running from build made by PyInstaller"""
auto_split_directory = os.path.dirname(sys.executable if FROZEN else os.path.abspath(__file__))
"""The directory of either the AutoSplit executable or AutoSplit.py"""

# Shared strings
# Check `excludeBuildNumber` during workflow dispatch build generate a clean version number
AUTOSPLIT_VERSION = "2.3.2" + (f"-{AUTOSPLIT_BUILD_NUMBER}" if AUTOSPLIT_BUILD_NUMBER else "")
"""AutoSplit Version number"""
GITHUB_REPOSITORY = AUTOSPLIT_GITHUB_REPOSITORY
