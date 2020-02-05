def threshold_from_filename(filename):
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
    except:
        return None

    # Check to make sure if it is a valid threshold
    if (threshold > 1.0 or threshold < 0.0):
        return None
    else:
        return threshold

def pause_from_filename(filename):
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
    except:
        return None

    # Pause times should always be positive or zero
    if (pause < 0.0):
        return None
    else:
        return pause

def delay_from_filename(filename):
    """
    Retrieve the delay time from the filename, if there is no delay time or the delay time
    isn't a valid number, then None is returned

    @param filename: String containing the file's name
    @return: A valid delay time, if not then 0
    """

    # Check to make sure there is a valid delay time between brackets
    # of the filename
    try:
        delay = float(filename.split('#', 1)[1].split('#')[0])
    except:
        return 0

    # Delay times should always be positive or zero
    if (delay < 0):
        return 0
    else:
        return delay

def loop_from_filename(filename):
    """
    Retrieve the number of loops from filename, if there is no loop number or the loop number isn't valid,
    then 1 is returned.

    @param filename: String containing the file's name
    @return: A valid loop number, if not then 1
    """

    # Check to make sure there is a valid loop number between at's
    # of the filename
    try:
        loop = int(filename.split('@', 1)[1].split('@')[0])
    except:
        return 1

    # Make loop number 1 if it is less than 1
    if (loop < 1):
        return 1
    else:
        return loop

def flags_from_filename(filename):
    """
    Retrieve the flags from the filename, if there are no flags then 0 is returned

    @param filename: String containing the file's name
    @return: The flags as an integer, if invalid flags are found it returns 0
    """

    """
    List of flags:
    'd' = dummy, do nothing when this split is found
    'm' = mask, use a mask when comparing this split
    'b' = below threshold, after threshold is met, split when it goes below the threhsold.
    'p' = pause, hit pause key when this split is found
    """

    # Check to make sure there are flags between curly braces
    # of the filename
    try:
        flags_str = filename.split('{', 1)[1].split('}')[0]
    except:
        return 0

    DUMMY_FLAG = 1 << 0
    MASK_FLAG = 1 << 1
    BELOW_FLAG = 1 << 2
    PAUSE_FLAG = 1 << 3

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

def is_reset_image(filename):
    """
    Checks if the image is used for resetting

    @param filename: String containing the file's name
    @return: True if its a reset image
    """
    return ('RESET' in filename.upper())
