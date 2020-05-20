# Error messages

# The reason why the errors don't end with "_ERROR" is
# because the file itself is already called "errors"

SPLIT_IMAGES_DIRECTORY = "No valid split image folder is selected."

NO_SPLIT_IMAGES = "Your split image folder does not contain any splits."

IMAGE_TYPE = '"%s" is not a valid image file or the full image file path contains a special character.'

REGION = "No region is selected. Select a region or reload settings while region window is open."

REGION_SIZE = "Width and height cannot be 0. Please select a larger region."

SPLIT_HOTKEY = "No split hotkey has been set."

ALPHA_CHANNEL = '"%s" is marked with mask flag but it does not have transparency.'

ALIGN_REGION_IMAGE_TYPE = "File is not a valid image file."

ALIGNMENT_NOT_MATCHED = "No area in capture region matched reference image. Alignment failed."

MULTIPLE_IMAGES_WITH_KEYWORD = 'Only one image with the keyword "%s" is allowed.'

FORCED_THRESHOLD = 'The image with the keyword "%s" must have a custom threshold. Please set one and check that it is valid.'

RESET_HOTKEY = "Your split image folder contains a reset image, but no reset hotkey is set."

PAUSE_HOTKEY = "Your split image folder contains an image marked with pause flag, but no pause hotkey is set."

SETTINGS_NOT_FOUND = "No settings file found. The settings file is saved when the program is closed."

INVALID_SETTINGS = "The settings file is invalid."

LAST_IMAGE_HAS_INCLUDE_NEXT_FLAG = "The last split image in the image folder is marked with include next flag."

IMAGE_HAS_INCLUDE_NEXT_FLAG = 'The image with the keyword "%s" is marked with include next flag.'

INCLUDE_NEXT_FLAG_WITH_LOOP = "Your split image folder contains an image marked with include next flag followed by an image with a loop value greater than 1."

NO_START_IMAGE = 'Your split image folder does not contain an image with the keyword "start_auto_splitter".'
