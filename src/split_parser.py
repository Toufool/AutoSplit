import os
from typing import List

import cv2

from AutoSplit import AutoSplit
import error_messages


[DUMMY_FLAG,
 # Legacy flag. Allows support for {md}, {mp}, or {mb} flags previously required to detect transparency.
 MASK_FLAG,
 BELOW_FLAG,
 PAUSE_FLAG,
 *_] = [1 << i for i in range(31)]


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
        threshold = float(filename.split('(', 1)[1].split(')')[0])
    except Exception:
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
        pause = float(filename.split('[', 1)[1].split(']')[0])
    except Exception:
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
        delay = float(filename.split('#', 1)[1].split('#')[0])
    except Exception:
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
        loop = int(filename.split('@', 1)[1].split('@')[0])
    except Exception:
        return 1

    # Loop should always be positive
    return loop if loop >= 1 else 1


def flags_from_filename(filename: str):
    """
    Retrieve the flags from the filename, if there are no flags then 0 is returned

    @param filename: String containing the file's name
    @return: The flags as an integer, if invalid flags are found it returns 0

    List of flags:
    'd' = dummy, do nothing when this split is found
    'b' = below threshold, after threshold is met, split when it goes below the threhsold.
    'p' = pause, hit pause key when this split is found
    """

    # Check to make sure there are flags between curly braces
    # of the filename
    try:
        flags_str = filename.split('{', 1)[1].split('}')[0]
    except Exception:
        return 0

    flags = 0x00

    for c in flags_str:
        if c.upper() == 'D':
            flags |= DUMMY_FLAG
        elif c.upper() == 'M':
            flags |= MASK_FLAG
        elif c.upper() == 'B':
            flags |= BELOW_FLAG
        elif c.upper() == 'P':
            flags |= PAUSE_FLAG
        else:
            # An invalid flag was caught, this filename was written incorrectly
            # return 0. We don't want to interpret any misleading filenames
            return 0

    # Check for any conflicting flags that were set
    # For instance, we can't have a dummy split also pause
    if (flags & DUMMY_FLAG == DUMMY_FLAG) and (flags & PAUSE_FLAG == PAUSE_FLAG):
        return 0

    return flags


def is_reset_image(filename: str):
    """
    Checks if the image is used for resetting

    @param filename: String containing the file's name
    @return: True if its a reset image
    """
    return 'RESET' in filename.upper()


def is_start_auto_splitter_image(filename: str):
    """
    Checks if the image is used to start AutoSplit

    @param filename: String containing the file's name
    @return: True if its a reset image
    """
    return 'START_AUTO_SPLITTER' in filename.upper()


def removeStartAutoSplitterImage(split_image_filenames: List[str]):
    start_auto_splitter_image_file = None
    for image in split_image_filenames:
        if is_start_auto_splitter_image(image):
            start_auto_splitter_image_file = image
            break

    if start_auto_splitter_image_file is None:
        return

    split_image_filenames.remove(start_auto_splitter_image_file)


# TODO: When split, reset and start image are all a proper class
# let's also extract reset and start from the list here and return them
def validate_images_before_parsing(autosplit: AutoSplit):
    already_found_reset_image = False
    already_found_start_image = False
    # Make sure that each of the images follows the guidelines for correct format
    # according to all of the settings selected by the user.
    for image in autosplit.split_image_filenames:
        # Test for image without transparency
        if (cv2.imread(os.path.join(autosplit.split_image_directory, image), cv2.IMREAD_COLOR) is None
                # Test for image with transparency
                and cv2.imread(os.path.join(autosplit.split_image_directory, image), cv2.IMREAD_UNCHANGED) is None):
            # Opencv couldn't open this file as an image, this isn't a correct
            # file format that is supported
            autosplit.guiChangesOnReset()
            error_messages.imageTypeError(image)
            return

        # error out if there is a {p} flag but no pause hotkey set and is not auto controlled.
        if (not autosplit.pausehotkeyLineEdit.text()
                and flags_from_filename(image) & PAUSE_FLAG == PAUSE_FLAG
                and not autosplit.is_auto_controlled):
            autosplit.guiChangesOnReset()
            error_messages.pauseHotkeyError()
            return

        # Check that there's only one reset image
        if is_reset_image(image):
            # If there is no reset hotkey set but a reset image is present, and is not auto controlled, throw an error.
            if not autosplit.resetLineEdit.text() and not autosplit.is_auto_controlled:
                autosplit.guiChangesOnReset()
                error_messages.resetHotkeyError()
                return
            if already_found_reset_image:
                autosplit.guiChangesOnReset()
                error_messages.multipleKeywordImagesError('reset')
                return
            already_found_reset_image = True

        # Check that there's only one auto_start_autosplitter image
        if is_start_auto_splitter_image(image):
            if already_found_start_image:
                autosplit.guiChangesOnReset()
                error_messages.multipleKeywordImagesError('start_auto_splitter')
                return
            already_found_start_image = True
