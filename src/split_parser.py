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

def flags_from_filename(filename):
    """
    Retrieve the flags from the filename, if there are no flags then None is returned

    @param filename: String containing the file's name
    @return: The flags as a string, if not then None
    """

    """
    List of flags:
    'd' = dummy, do nothing when this split is found
    'm' = mask, use a mask when comparing this split (TBD!!)
    'p' = pause, hit pause key when this split is found
    """

    # Check to make sure there are flags between curly braces
    # of the filename
    try:
        #TODO: If there are no closing brackets this could catch the rest of the filename
        # that can catch flags in the filename extension or any other substrings within
        # the file's name.
        flags = filename.split('{', 1)[1].split('}')[0]
    except:
        return None

    """
    TODO: Perhaps instead of sending a string, which can send flags that don't exist
    maybe we can convert them to an integer for easier use. Any unxpected characters
    can cause None to return. Also, this would help prevent conflicting flags, for
    example you can't have a dummy split also be a pause split.

    DUMMY_FLAG = 1 << 0
    MASK_FLAG = 1 << 1
    PAUSE_FLAG = 1 << 2
    """

    return flags
