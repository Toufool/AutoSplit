from __future__ import annotations

import os
import sys
from collections.abc import Callable
from functools import partial
from stat import UF_HIDDEN
from typing import TYPE_CHECKING, TypeVar

import error_messages
from AutoSplitImage import RESET_KEYWORD, START_KEYWORD, AutoSplitImage, ImageType
from utils import is_valid_image

if sys.platform == "win32":
    from stat import FILE_ATTRIBUTE_HIDDEN, FILE_ATTRIBUTE_SYSTEM


if TYPE_CHECKING:
    from _typeshed import StrPath

    from AutoSplit import AutoSplit

(
    DUMMY_FLAG,
    BELOW_FLAG,
    PAUSE_FLAG,
    *_,
) = tuple(1 << i for i in range(31))  # 32 bits of flags

FileFlagValueT = TypeVar("FileFlagValueT", str, int, float)

# Note, the following symbols cannot be used in a filename:
# / \ : * ? " < > |


def __value_from_filename(
    filename: str,
    delimiters: str,
    default_value: FileFlagValueT,
) -> FileFlagValueT:
    if len(delimiters) != 2:
        raise ValueError("delimiters parameter must contain exactly 2 characters")
    try:
        string_value = filename.split(delimiters[0], 1)[1].split(delimiters[1])[0]
        value = type(default_value)(string_value)
    except (IndexError, ValueError):
        return default_value
    else:
        return value


def threshold_from_filename(filename: str):
    """
    Retrieve the threshold from the filename.
    If there is no threshold or the threshold doesn't meet the requirements of being [0, 1],
    then None is returned.

    @param filename: String containing the file's name
    @return: A valid threshold, if not then None
    """
    # Check to make sure there is a valid floating point number between
    # parentheses of the filename
    value = __value_from_filename(filename, "()", -1.0)

    # Check to make sure if it is a valid threshold
    return value if 0 <= value <= 1 else None


def pause_from_filename(filename: str):
    """
    Retrieve the pause time from the filename,
    if there is no pause time or the pause time isn't a valid positive number or 0,
    then None is returned.

    @param filename: String containing the file's name
    @return: A valid pause time, if not then None
    """
    # Check to make sure there is a valid pause time between brackets
    # of the filename
    value = __value_from_filename(filename, "[]", -1.0)

    # Pause times should always be positive or zero
    return value if value >= 0 else None


def delay_time_from_filename(filename: str):
    """
    Retrieve the delay time from the filename.
    If there is no delay time or the delay time isn't a valid positive number or 0 number,
    then None is returned.

    @param filename: String containing the file's name
    @return: A valid delay time, if not then none
    """
    # Check to make sure there is a valid delay time between brackets
    # of the filename
    value = __value_from_filename(filename, "##", -1)

    # Delay times should always be positive or zero
    return value if value >= 0 else None


def loop_from_filename(filename: str):
    """
    Retrieve the number of loops from filename.
    If there is no loop number or the loop number isn't valid, then 1 is returned.

    @param filename: String containing the file's name
    @return: A valid loop number, if not then 1
    """
    # Check to make sure there is a valid delay time between brackets
    # of the filename
    value = __value_from_filename(filename, "@@", 1)

    # Loop should always be positive
    return max(value, 1)


def comparison_method_from_filename(filename: str):
    """
    Retrieve the comparison method index from filename.
    If there is no comparison method or the index isn't valid, then None is returned.

    @param filename: String containing the file's name
    @return: A valid comparison method index, if not then none
    """
    # Check to make sure there is a valid delay time between brackets
    # of the filename
    value = __value_from_filename(filename, "^^", -1)

    # Comparison method should always be positive or zero
    return value if value >= 0 else None


def flags_from_filename(filename: str):
    """
    Retrieve the flags from the filename.
    If there are no flags, then 0 is returned.

    @param filename: String containing the file's name
    @return: The flags as an integer, if invalid flags are found it returns 0

    list of flags:
    "d" = dummy, do nothing when this split is found
    "b" = below threshold, after threshold is met, split when it goes below the threhsold.
    "p" = pause, hit pause key when this split is found
    """
    # Check to make sure there are flags between curly braces
    # of the filename
    flags_str = __value_from_filename(filename, "{}", "")

    if not flags_str:
        return 0

    flags = 0x00

    for flag_str in flags_str:
        match flag_str.upper():
            case "D":
                flags |= DUMMY_FLAG
            case "B":
                flags |= BELOW_FLAG
            case "P":
                flags |= PAUSE_FLAG
            # Legacy flags
            case "M":
                continue
            # An invalid flag was caught, this filename was written incorrectly return 0.
            # We don't want to interpret any misleading filenames
            case _:
                return 0

    # Check for any conflicting flags that were set
    # For instance, we can't have a dummy split also pause
    if (flags & DUMMY_FLAG == DUMMY_FLAG) and (flags & PAUSE_FLAG == PAUSE_FLAG):
        return 0

    return flags


def __pop_image_type(split_image: list[AutoSplitImage], image_type: ImageType):
    for image in split_image:
        if image.image_type == image_type:
            split_image.remove(image)
            return image

    return None


def validate_before_parsing(autosplit: AutoSplit, *, show_error: bool = True):
    error = None
    split_image_directory = autosplit.settings_dict["split_image_directory"]
    if not split_image_directory:
        error = error_messages.split_image_directory
    elif not os.path.isdir(split_image_directory):
        error = partial(error_messages.invalid_directory, split_image_directory)
    elif not autosplit.capture_method.check_selected_region_exists():
        error = error_messages.region
    if error and show_error:
        error()
    return not error


def is_user_file(path: StrPath):
    """Returns False for hidden files, system files and folders."""
    if os.path.isdir(path) or os.path.basename(path).startswith("."):
        return False
    if sys.platform == "linux":
        return True
    stat_result = os.stat(path)
    if sys.platform == "win32":
        return not (
            (stat_result.st_file_attributes & FILE_ATTRIBUTE_SYSTEM)
            | (stat_result.st_file_attributes & FILE_ATTRIBUTE_HIDDEN)
        )
    if sys.platform == "darwin":
        return not (stat_result.st_mode & UF_HIDDEN)
    return True


def __get_images_from_directory(directory: StrPath):
    """
    Returns a list of AutoSplitImage parsed from a directory.
    Hidden files, system files and folders are silently ignored.
    """
    file_paths = [
        os.path.join(directory, filename)  # format: skip
        for filename in os.listdir(directory)
    ]
    filtered_image_paths = [
        image_path  # format: skip
        for image_path in file_paths
        if is_user_file(image_path)
    ]
    # On Linux, os.listdir doesn't list files in alphanumerical order.
    # On Windows, os.listdir is already alphanumerical, but let's ensure consistency across OSes.
    filtered_image_paths.sort()
    return [AutoSplitImage(image_path) for image_path in filtered_image_paths]


def parse_and_validate_images(autosplit: AutoSplit):
    all_images = __get_images_from_directory(autosplit.settings_dict["split_image_directory"])
    # Find non-split images and then remove them from the list
    start_image = __pop_image_type(all_images, ImageType.START)
    reset_image = __pop_image_type(all_images, ImageType.RESET)
    split_images = all_images

    error_message: Callable[[], object] | None = None

    if not split_images:
        error_message = error_messages.no_split_image

    # If there is no start hotkey set but a Start Image is present,
    # and is not auto controlled, throw an error.
    elif (
        start_image
        and not autosplit.settings_dict["split_hotkey"]
        and not autosplit.is_auto_controlled
    ):
        error_message = error_messages.load_start_image

    # If there is no reset hotkey set but a Reset Image is present,
    # and is not auto controlled, throw an error.
    elif (
        reset_image
        and not autosplit.settings_dict["reset_hotkey"]
        and not autosplit.is_auto_controlled
    ):
        error_message = error_messages.reset_hotkey

    # Make sure that each of the images follows the guidelines for correct format
    # according to all of the settings selected by the user.
    else:
        for image in split_images:
            # Test for image without transparency
            if not image.is_ocr and not is_valid_image(image.byte_array):
                error_message = partial(error_messages.image_validity, image.filename)
                break

            # error out if there is a {p} flag but no pause hotkey set and is not auto controlled.
            if (
                not autosplit.settings_dict["pause_hotkey"]
                and image.check_flag(PAUSE_FLAG)
                and not autosplit.is_auto_controlled
            ):
                error_message = error_messages.pause_hotkey
                break

            # Check that there's only one Reset Image
            if image.image_type == ImageType.RESET:
                error_message = lambda: error_messages.multiple_keyword_images(RESET_KEYWORD)  # noqa: E731
                break

            # Check that there's only one Start Image
            if image.image_type == ImageType.START:
                error_message = lambda: error_messages.multiple_keyword_images(START_KEYWORD)  # noqa: E731
                break

    if error_message:
        autosplit.start_image = None
        autosplit.reset_image = None
        autosplit.split_images = []
        autosplit.gui_changes_on_reset()
        error_message()
        return False

    autosplit.start_image = start_image
    autosplit.reset_image = reset_image
    autosplit.split_images = split_images
    return True
