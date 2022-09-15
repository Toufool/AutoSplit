from __future__ import annotations

import os
from enum import Enum
from typing import TYPE_CHECKING

import cv2
import numpy as np
from win32con import MAXBYTE

import error_messages
from compare import check_if_image_has_transparency, compare_histograms, compare_l2_norm, compare_phash
from utils import is_valid_image

if TYPE_CHECKING:
    from AutoSplit import AutoSplit

# Resize to these width and height so that FPS performance increases
COMPARISON_RESIZE_WIDTH = 320
COMPARISON_RESIZE_HEIGHT = 240
COMPARISON_RESIZE = (COMPARISON_RESIZE_WIDTH, COMPARISON_RESIZE_HEIGHT)
LOWER_BOUND = np.array([0, 0, 0, 1], dtype="uint8")
UPPER_BOUND = np.array([MAXBYTE, MAXBYTE, MAXBYTE, MAXBYTE], dtype="uint8")
START_KEYWORD = "start_auto_splitter"
RESET_KEYWORD = "reset"


class ImageType(Enum):
    SPLIT = 0
    RESET = 1
    START = 2


class AutoSplitImage():
    path: str
    filename: str
    flags: int
    loops: int
    image_type: ImageType
    byte_array: cv2.Mat | None = None
    mask: cv2.Mat | None = None
    # This value is internal, check for mask instead
    _has_transparency = False
    # These values should be overriden by some Defaults if None. Use getters instead
    __delay_time: float | None = None
    __comparison_method: int | None = None
    __pause_time: float | None = None
    __similarity_threshold: float | None = None

    def get_delay_time(self, default: AutoSplit | int):
        """
        Get image's delay time or fallback to the default value from spinbox
        """
        default_value = default \
            if isinstance(default, int) \
            else default.settings_dict["default_delay_time"]
        return default_value if self.__delay_time is None else self.__delay_time

    def __get_comparison_method(self, default: AutoSplit | int):
        """
        Get image's comparison or fallback to the default value from combobox
        """
        default_value = default \
            if isinstance(default, int) \
            else default.settings_dict["default_comparison_method"]
        return default_value if self.__comparison_method is None else self.__comparison_method

    def get_pause_time(self, default: AutoSplit | float):
        """
        Get image's pause time or fallback to the default value from spinbox
        """
        default_value = default \
            if isinstance(default, float) \
            else default.settings_dict["default_pause_time"]
        return default_value if self.__pause_time is None else self.__pause_time

    def get_similarity_threshold(self, default: AutoSplit | float):
        """
        Get image's similarity threshold or fallback to the default value from spinbox
        """
        default_value = default \
            if isinstance(default, float) \
            else default.settings_dict["default_similarity_threshold"]
        return default_value if self.__similarity_threshold is None else self.__similarity_threshold

    def __init__(self, path: str):
        self.path = path
        self.filename = os.path.split(path)[-1].lower()
        self.flags = flags_from_filename(self.filename)
        self.loops = loop_from_filename(self.filename)
        self.__delay_time = delay_time_from_filename(self.filename)
        self.__comparison_method = comparison_method_from_filename(self.filename)
        self.__pause_time = pause_from_filename(self.filename)
        self.__similarity_threshold = threshold_from_filename(self.filename)
        self.__read_image_bytes(path)

        if START_KEYWORD in self.filename:
            self.image_type = ImageType.START
        elif RESET_KEYWORD in self.filename:
            self.image_type = ImageType.RESET
        else:
            self.image_type = ImageType.SPLIT

    def __read_image_bytes(self, path: str):
        image = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if not is_valid_image(image):
            self.byte_array = None
            error_messages.image_type(path)
            return

        image = cv2.resize(image, COMPARISON_RESIZE, interpolation=cv2.INTER_NEAREST)
        self._has_transparency = check_if_image_has_transparency(image)
        # If image has transparency, create a mask
        if self._has_transparency:
            # Create mask based on resized, nearest neighbor interpolated split image
            self.mask = cv2.inRange(image, LOWER_BOUND, UPPER_BOUND)
        # Add Alpha channel if missing
        elif image.shape[2] == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)

        self.byte_array = image

    def check_flag(self, flag: int):
        return self.flags & flag == flag

    def compare_with_capture(
        self,
        default: AutoSplit | int,
        capture: cv2.Mat | None,
    ):
        """
        Compare image with capture using image's comparison method. Falls back to combobox
        """

        if not is_valid_image(self.byte_array) or not is_valid_image(capture):
            return 0.0
        comparison_method = self.__get_comparison_method(default)
        if comparison_method == 0:
            return compare_l2_norm(self.byte_array, capture, self.mask)
        if comparison_method == 1:
            return compare_histograms(self.byte_array, capture, self.mask)
        if comparison_method == 2:
            return compare_phash(self.byte_array, capture, self.mask)
        return 0.0


if True:  # pylint: disable=using-constant-test
    from split_parser import (
        comparison_method_from_filename, delay_time_from_filename, flags_from_filename, loop_from_filename,
        pause_from_filename, threshold_from_filename,
    )
