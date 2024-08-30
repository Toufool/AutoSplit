import os
from enum import IntEnum, auto
from math import sqrt
from typing import TYPE_CHECKING

import cv2
import numpy as np
import toml
from cv2.typing import MatLike

import error_messages
from compare import (
    check_if_image_has_transparency,
    extract_and_compare_text,
    get_comparison_method_by_index,
)
from utils import (
    BGR_CHANNEL_COUNT,
    MAXBYTE,
    TESSERACT_PATH,
    ColorChannel,
    ImageShape,
    imread,
    is_valid_image,
)

if TYPE_CHECKING:
    from AutoSplit import AutoSplit


# Resize to these width and height so that FPS performance increases
COMPARISON_RESIZE_WIDTH = 320
COMPARISON_RESIZE_HEIGHT = 240
COMPARISON_RESIZE = (COMPARISON_RESIZE_WIDTH, COMPARISON_RESIZE_HEIGHT)
COMPARISON_RESIZE_AREA = COMPARISON_RESIZE_WIDTH * COMPARISON_RESIZE_HEIGHT
MASK_LOWER_BOUND = np.array([0, 0, 0, 1], dtype=np.uint8)
MASK_UPPER_BOUND = np.array([MAXBYTE, MAXBYTE, MAXBYTE, MAXBYTE], dtype=np.uint8)
START_KEYWORD = "start_auto_splitter"
RESET_KEYWORD = "reset"


class ImageType(IntEnum):
    SPLIT = auto()
    RESET = auto()
    START = auto()


class AutoSplitImage:
    image_type: ImageType
    byte_array: MatLike | None = None
    mask: MatLike | None = None
    # This value is internal, check for mask instead
    _has_transparency = False
    # These values should be overridden by some Defaults if None. Use getters instead
    __delay_time: float | None = None
    __comparison_method: int | None = None
    __pause_time: float | None = None
    __similarity_threshold: float | None = None
    __rect = (0, 0, 1, 1)
    __fps_limit = 0

    @property
    def is_ocr(self):
        """
        Whether a "split image" is actually for Optical Text Recognition
        based on whether there's any text strings to search for.
        """
        return bool(self.texts)

    def get_delay_time(self, default: "AutoSplit | int"):
        """Get image's delay time or fallback to the default value from spinbox."""
        if self.__delay_time is not None:
            return self.__delay_time
        if isinstance(default, int):
            return default
        return default.settings_dict["default_delay_time"]

    def __get_comparison_method_index(self, default: "AutoSplit | int"):
        """Get image's comparison or fallback to the default value from combobox."""
        if self.__comparison_method is not None:
            return self.__comparison_method
        if isinstance(default, int):
            return default
        return default.settings_dict["default_comparison_method"]

    def get_pause_time(self, default: "AutoSplit | float"):
        """Get image's pause time or fallback to the default value from spinbox."""
        if self.__pause_time is not None:
            return self.__pause_time
        if isinstance(default, (float, int)):
            return default
        return default.settings_dict["default_pause_time"]

    def get_similarity_threshold(self, default: "AutoSplit | float"):
        """Get image's similarity threshold or fallback to the default value from spinbox."""
        if self.__similarity_threshold is not None:
            return self.__similarity_threshold
        if isinstance(default, (float, int)):
            return default
        return default.settings_dict["default_similarity_threshold"]

    def get_fps_limit(self, default: "AutoSplit"):
        """Get image's fps limit or fallback to the default value from spinbox."""
        if self.__fps_limit != 0:
            return self.__fps_limit
        return default.settings_dict["fps_limit"]

    def __init__(self, path: str):
        self.path = path
        self.filename = os.path.split(path)[-1].lower()
        self.flags = flags_from_filename(self.filename)
        self.loops = loop_from_filename(self.filename)
        self.__delay_time = delay_time_from_filename(self.filename)
        self.__comparison_method = comparison_method_from_filename(self.filename)
        self.__pause_time = pause_from_filename(self.filename)
        self.__similarity_threshold = threshold_from_filename(self.filename)
        self.texts: list[str] = []
        self.__ocr_comparison_methods: list[int] = []
        if path.endswith("txt"):
            self.__parse_text_file(path)
        else:
            self.__read_image_bytes(path)

        if START_KEYWORD in self.filename:
            self.image_type = ImageType.START
        elif RESET_KEYWORD in self.filename:
            self.image_type = ImageType.RESET
        else:
            self.image_type = ImageType.SPLIT

    def __parse_text_file(self, path: str):
        if not TESSERACT_PATH:
            error_messages.tesseract_missing(path)
            return

        with open(path, encoding="utf-8") as f:
            data = toml.load(f)

        self.texts = [text.lower().strip() for text in data["texts"]]
        self.__rect = (data["left"], data["right"], data["top"], data["bottom"])
        self.__ocr_comparison_methods = data.get("methods", [0])
        self.__fps_limit = data.get("fps_limit", 0)

        if self.__validate_ocr():
            error_messages.wrong_ocr_values(path)
            return

    def __validate_ocr(self):
        values = [*self.__rect, *self.__ocr_comparison_methods, self.__fps_limit]
        return (
            all(value >= 0 for value in values)  # Check for invalid negative values
            and self.__rect[1] > self.__rect[0]
            and self.__rect[3] > self.__rect[2]
        )

    def __read_image_bytes(self, path: str):
        image = imread(path, cv2.IMREAD_UNCHANGED)
        if not is_valid_image(image):
            self.byte_array = None
            error_messages.image_type(path)
            return

        self._has_transparency = check_if_image_has_transparency(image)
        # If image has transparency, create a mask
        if self._has_transparency:
            # Adaptively determine the target size according to
            # the number of nonzero elements in the alpha channel of the split image.
            # This may result in images bigger than COMPARISON_RESIZE if there's plenty of transparency. # noqa: E501
            # Which wouldn't incur any performance loss in methods where masked regions are ignored.
            scale = min(
                1,
                sqrt(COMPARISON_RESIZE_AREA / cv2.countNonZero(image[:, :, ColorChannel.Alpha])),
            )

            image = cv2.resize(
                image,
                dsize=None,
                fx=scale,
                fy=scale,
                interpolation=cv2.INTER_NEAREST,
            )

            # Mask based on adaptively resized, nearest neighbor interpolated split image
            self.mask = cv2.inRange(image, MASK_LOWER_BOUND, MASK_UPPER_BOUND)
        else:
            image = cv2.resize(image, COMPARISON_RESIZE, interpolation=cv2.INTER_NEAREST)
            # Add Alpha channel if missing
            if image.shape[ImageShape.Channels] == BGR_CHANNEL_COUNT:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)

        self.byte_array = image

    def check_flag(self, flag: int):
        return self.flags & flag == flag

    def compare_with_capture(self, default: "AutoSplit | int", capture: MatLike | None):
        """
        Compare image with capture using image's comparison method. Falls back to combobox.

        For OCR text files:
            extract image text from rectangle position and compare it with the expected string.
        """
        if not is_valid_image(capture):
            return 0.0

        if self.is_ocr:
            return extract_and_compare_text(
                capture[
                    self.__rect[2] : self.__rect[3],
                    self.__rect[0] : self.__rect[1],
                ],
                self.texts,
                self.__ocr_comparison_methods,
            )

        if not is_valid_image(self.byte_array):
            return 0.0
        resized_capture = cv2.resize(capture, self.byte_array.shape[1::-1], interpolation=cv2.INTER_NEAREST)

        return get_comparison_method_by_index(
            self.__get_comparison_method_index(default),
        )(
            self.byte_array,
            resized_capture,
            self.mask,
        )


if True:
    from split_parser import (
        comparison_method_from_filename,
        delay_time_from_filename,
        flags_from_filename,
        loop_from_filename,
        pause_from_filename,
        threshold_from_filename,
    )
