import cv2
import numpy as np

class SplitImage:

    def __init__(self, path, filename):
        self.path = path + filename
        self.filename = filename

        # For the {b} flag
        self.split_below_threshold = False

        # The index of split_images where the split is found that AutoSplit should jump to
        # when undoing/skipping a split
        self.undo_image_index = None
        self.skip_image_index = None

        # Retrieve the threshold from the filename, if there is no threshold or the threshold
        # doesn't meet the requirements of being between 0.0 and 1.0, then it is set to None

        # Check to make sure there is a valid floating point number between
        # parentheses of the filename
        try:
            self.threshold = float(self.filename.split('(', 1)[1].split(')')[0])

            # Check to make sure if it is a valid threshold
            if (self.threshold > 1.0 or self.threshold < 0.0):
                raise ValueError
        except:
            self.threshold = None


        # Retrieve the pause time from the filename, if there is no pause time or the pause time
        # isn't a valid number, then it is set to None

        # Check to make sure there is a valid pause time between brackets
        # of the filename
        try:
            self.pause = float(self.filename.split('[', 1)[1].split(']')[0])

            # Pause times should always be positive or zero
            if (self.pause < 0.0):
                raise ValueError
        except:
            self.pause = None


        # Retrieve the delay time from the filename, if there is no delay time or the delay time
        # isn't a valid number, then it is set to 0

        # Check to make sure there is a valid delay time between brackets
        # of the filename
        try:
            self.delay = float(self.filename.split('#', 1)[1].split('#')[0])

            # Delay times should always be positive or zero
            if (self.delay < 0):
                raise ValueError
        except:
            self.delay = 0


        # Retrieve the number of loops from filename, if there is no loop number or the loop
        # number isn't valid, then it is set to 1

        # Check to make sure there is a valid loop number between at's
        # of the filename
        try:
            self.loop = int(self.filename.split('@', 1)[1].split('@')[0])

            # Make loop number 1 if it is less than 1
            if (self.loop < 1):
                raise ValueError
        except:
            self.loop = 1


        # Retrieve the flags from the filename, if there are no flags, then it is set to 0 (no flags set)

        # List of flags:
        # 'd' = dummy, do nothing when this split is found
        # 'm' = mask, use a mask when comparing this split
        # 'b' = below threshold, after threshold is met, split when it goes below the threshold
        # 'p' = pause, hit pause key when this split is found
        # 'n' = include next, compares live image with both this image and the one after that simultaneously
        # 'u' = undo, means that this is the split in this split group that is compared to after you hit undo in the next split group

        # Check to make sure there are flags between curly braces
        # of the filename and they are all valid
        try:
            self.flags = 0

            for c in self.filename.split('{', 1)[1].split('}')[0].upper():
                if c == 'D':
                    self.flags |= 1 << 0 # Dummy flag {d}:           0x01
                elif c == 'M':
                    self.flags |= 1 << 1 # Mask flag {m}:            0x02
                elif c == 'B':
                    self.flags |= 1 << 2 # Below threshold flag {b}: 0x04
                elif c == 'P':
                    self.flags |= 1 << 3 # Pause flag {p}:           0x08
                elif c == 'N':
                    self.flags |= 1 << 4 # Include next flag {n}:    0x10
                elif c == 'U':
                    self.flags |= 1 << 5 # Undo flag {u}:            0x20
                else:
                    # An invalid flag was caught, this filename was written incorrectly.
                    # Set it to 0, we don't want to interpret any misleading filenames
                    raise ValueError
        except:
            self.flags = 0


        # Checks if the image is used for resetting

        self.is_reset_image = ('RESET' in self.filename.upper())

    def get_image(self, resize_width, resize_height):
        if (self.flags & 0x02 == 0x02):
            # Create mask based on resized, nearest neighbor interpolated split image
            self.image = cv2.imread(self.path, cv2.IMREAD_UNCHANGED)
            self.image = cv2.resize(self.image, (resize_width, resize_height),
                                          interpolation=cv2.INTER_NEAREST)
            lower = np.array([0, 0, 0, 1], dtype="uint8")
            upper = np.array([255, 255, 255, 255], dtype="uint8")
            self.mask = cv2.inRange(self.image, lower, upper)

            # Set split image as BGR
            self.image = cv2.cvtColor(self.image, cv2.COLOR_BGRA2BGR)

        # Else if there is no mask flag, open image normally. don't interpolate nearest neighbor here so setups before 1.2.0 still work.
        else:
            self.image = cv2.imread(self.path, cv2.IMREAD_COLOR)
            self.image = cv2.resize(self.image, (resize_width, resize_height))
            self.mask = None

        return image
