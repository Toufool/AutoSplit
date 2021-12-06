from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from AutoSplit import AutoSplit

import os

import error_messages
from AutoSplitImage import AutoSplitImage, ImageType


[DUMMY_FLAG,
 BELOW_FLAG,
 PAUSE_FLAG,
 *_] = [1 << i for i in range(31)]  # 32 bits of flags


def threshold_from_filename(filename: str):
    """
    Retrieve the threshold from the filename, if there is no threshold or the threshold
    doesn't meet the requirements of being between 0.0 and 1.0, then None is returned.

    @param filename: String containing the file's name
    @return: A valid threshold, if not then None
    """

    # Check to make sure there is a valid floating point number between
    # parentheses of the filename
    try:
        threshold = float(filename.split("(", 1)[1].split(")")[0])
    except (IndexError, ValueError):
        return None

    # Check to make sure if it is a valid threshold
    return threshold if 0.0 < threshold < 1.0 else None


def pause_from_filename(filename: str):
    """
    Retrieve the pause time from the filename, if there is no pause time or the pause time
    isn't a valid number, then None is returned

    @param filename: String containing the file's name
    @return: A valid pause time, if not then None
    """

    # Check to make sure there is a valid pause time between brackets
    # of the filename
    try:
        pause = float(filename.split("[", 1)[1].split("]")[0])
    except (IndexError, ValueError):
        return None

    # Pause times should always be positive or zero
    return pause if pause >= 0.0 else None


def delay_from_filename(filename: str):
    """
    Retrieve the delay time from the filename, if there is no delay time or the delay time
    isn't a valid number, then 0 is returned

    @param filename: String containing the file's name
    @return: A valid delay time, if not then 0
    """

    # Check to make sure there is a valid delay time between brackets
    # of the filename
    try:
        delay = float(filename.split("#", 1)[1].split("#")[0])
    except (IndexError, ValueError):
        return 0.0

    # Delay times should always be positive or zero
    return delay if delay >= 0.0 else 0.0


def loop_from_filename(filename: str):
    """
    Retrieve the number of loops from filename, if there is no loop number or the loop number isn't valid,
    then 1 is returned.

    @param filename: String containing the file's name
    @return: A valid loop number, if not then 1
    """

    # Check to make sure there is a valid delay time between brackets
    # of the filename
    try:
        loop = int(filename.split("@", 1)[1].split("@")[0])
    except (IndexError, ValueError):
        return 1

    # Loop should always be positive
    return loop if loop >= 1 else 1


def flags_from_filename(filename: str):
    """
    Retrieve the flags from the filename, if there are no flags then 0 is returned

    @param filename: String containing the file's name
    @return: The flags as an integer, if invalid flags are found it returns 0

    list of flags:
    "d" = dummy, do nothing when this split is found
    "b" = below threshold, after threshold is met, split when it goes below the threhsold.
    "p" = pause, hit pause key when this split is found
    """

    # Check to make sure there are flags between curly braces
    # of the filename
    try:
        flags_str = filename.split("{", 1)[1].split("}")[0]
    except (IndexError, ValueError):
        return 0

    flags = 0x00

    for character in flags_str:
        character = character.upper()
        if character == "D":
            flags |= DUMMY_FLAG
        elif character == "B":
            flags |= BELOW_FLAG
        elif character == "P":
            flags |= PAUSE_FLAG
        # Legacy flags
        elif character == "M":
            continue
        else:
            # An invalid flag was caught, this filename was written incorrectly
            # return 0. We don't want to interpret any misleading filenames
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


def parse_and_validate_images(autosplit: AutoSplit):
    # Get split images
    all_images = [
        AutoSplitImage(os.path.join(autosplit.split_image_directory, image_name))
        for image_name
        in os.listdir(autosplit.split_image_directory)]

    # Find non-split images and then remove them from the list
    autosplit.start_image = __pop_image_type(all_images, ImageType.START)
    autosplit.reset_image = __pop_image_type(all_images, ImageType.RESET)
    autosplit.split_images = all_images

    # Make sure that each of the images follows the guidelines for correct format
    # according to all of the settings selected by the user.
    for image in autosplit.split_images:
        # Test for image without transparency
        if image.bytes is None:
            autosplit.gui_changes_on_reset()
            return False

        # error out if there is a {p} flag but no pause hotkey set and is not auto controlled.
        if (not autosplit.pause_hotkey_input.text()
                and image.check_flag(PAUSE_FLAG)
                and not autosplit.is_auto_controlled):
            autosplit.gui_changes_on_reset()
            error_messages.pause_hotkey()
            return False

        # Check that there's only one reset image
        if image.image_type == ImageType.RESET:
            # If there is no reset hotkey set but a reset image is present, and is not auto controlled, throw an error.
            if not autosplit.reset_input.text() and not autosplit.is_auto_controlled:
                autosplit.gui_changes_on_reset()
                error_messages.reset_hotkey()
                return False
            autosplit.gui_changes_on_reset()
            error_messages.multiple_keyword_images("reset")
            return False

        # Check that there's only one start image
        if image.image_type == ImageType.START:
            autosplit.gui_changes_on_reset()
            error_messages.multiple_keyword_images("start_auto_splitter")
            return False
    return True
