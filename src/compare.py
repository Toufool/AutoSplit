from collections.abc import Iterable
from math import sqrt

import cv2
import Levenshtein
import numpy as np
from cv2.typing import MatLike

from utils import (
    BGRA_CHANNEL_COUNT,
    MAXBYTE,
    ColorChannel,
    ImageShape,
    is_valid_image,
    run_tesseract,
)

MAXRANGE = MAXBYTE + 1
CHANNELS = (ColorChannel.Red.value, ColorChannel.Green.value, ColorChannel.Blue.value)
HISTOGRAM_SIZE = (8, 8, 8)
RANGES = (0, MAXRANGE, 0, MAXRANGE, 0, MAXRANGE)
MASK_SIZE_MULTIPLIER = ColorChannel.Alpha * MAXBYTE * MAXBYTE
MAX_VALUE = 1.0
CV2_PHASH_SIZE = 8


def compare_histograms(source: MatLike, capture: MatLike, mask: MatLike | None = None):
    """
    Compares two images by calculating their histograms, normalizing
    them, and then comparing them using Bhattacharyya distance.

    @param source: RGB or BGR image of any given width and height
    @param capture: An image matching the shape, dimensions and format of the source
    @param mask: An image matching the dimensions of the source, but 1 channel grayscale
    @return: The similarity between the histograms as a number 0 to 1.
    """
    source_hist = cv2.calcHist([source], CHANNELS, mask, HISTOGRAM_SIZE, RANGES)
    capture_hist = cv2.calcHist([capture], CHANNELS, mask, HISTOGRAM_SIZE, RANGES)

    cv2.normalize(source_hist, source_hist)
    cv2.normalize(capture_hist, capture_hist)

    return 1 - cv2.compareHist(source_hist, capture_hist, cv2.HISTCMP_BHATTACHARYYA)


def compare_l2_norm(source: MatLike, capture: MatLike, mask: MatLike | None = None):
    """
    Compares two images by calculating the L2 Error (square-root of sum of squared error)
    @param source: Image of any given shape
    @param capture: Image matching the dimensions of the source
    @param mask: An image matching the dimensions of the source, but 1 channel grayscale
    @return: The similarity between the images as a number 0 to 1.
    """
    error = cv2.norm(source, capture, cv2.NORM_L2, mask)

    # The L2 Error is summed across all pixels, so this normalizes
    max_error = (
        sqrt(source.size) * MAXBYTE
        if not is_valid_image(mask)
        else sqrt(cv2.countNonZero(mask) * MASK_SIZE_MULTIPLIER)
    )

    if not max_error:
        return 0.0
    return 1 - (error / max_error)


def compare_template(source: MatLike, capture: MatLike, mask: MatLike | None = None):
    """
    Checks if the source is located within the capture by using the sum of square differences.
    The mask is used to search for non-rectangular images within the capture.

    @param source: The subsection being searched for within the capture
    @param capture: Capture of an image larger than the source
    @param mask: The mask of the source with the same dimensions
    @return: The best similarity for a region found in the image. This is
    represented as a number from 0 to 1.
    """
    result = cv2.matchTemplate(capture, source, cv2.TM_SQDIFF, mask=mask)
    min_val, *_ = cv2.minMaxLoc(result)

    # matchTemplate returns the sum of square differences, this is the max
    # that the value can be. Used for normalizing from 0 to 1.
    max_error = (
        source.size * MAXBYTE * MAXBYTE  # fmt: skip
        if not is_valid_image(mask)
        else cv2.countNonZero(mask)
    )

    return 1 - (min_val / max_error)


# The old scipy-based implementation.
# Turns out this cuases an extra 25 MB build compared to opencv-contrib-python-headless
# # from scipy import fft
# def __cv2_scipy_compute_phash(image: MatLike, hash_size: int, highfreq_factor: int = 4):
#     """Implementation copied from https://github.com/JohannesBuchner/imagehash/blob/38005924fe9be17cfed145bbc6d83b09ef8be025/imagehash/__init__.py#L260 ."""  # noqa: E501
#     img_size = hash_size * highfreq_factor
#     image = cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)
#     image = cv2.resize(image, (img_size, img_size), interpolation=cv2.INTER_AREA)
#     dct = fft.dct(fft.dct(image, axis=0), axis=1)
#     dct_low_frequency = dct[:hash_size, :hash_size]
#     median = np.median(dct_low_frequency)
#     return dct_low_frequency > median
# def __cv2_phash(source: MatLike, capture: MatLike, hash_size: int = 8):
#     source_hash = __cv2_scipy_compute_phash(source, hash_size)
#     capture_hash = __cv2_scipy_compute_phash(capture, hash_size)
#     hash_diff = np.count_nonzero(source_hash != capture_hash)
#     return 1 - (hash_diff / 64.0)


def __cv2_phash(source: MatLike, capture: MatLike):
    """
    OpenCV has its own pHash comparison implementation in `cv2.img_hash`,
    but is inaccurate unless we precompute the size with a specific interpolation.

    See: https://github.com/opencv/opencv_contrib/issues/3295#issuecomment-1172878684
    """
    phash = cv2.img_hash.PHash.create()
    source = cv2.resize(source, (CV2_PHASH_SIZE, CV2_PHASH_SIZE), interpolation=cv2.INTER_AREA)
    capture = cv2.resize(capture, (CV2_PHASH_SIZE, CV2_PHASH_SIZE), interpolation=cv2.INTER_AREA)
    source_hash = phash.compute(source)
    capture_hash = phash.compute(capture)
    hash_diff = phash.compare(source_hash, capture_hash)
    return 1 - (hash_diff / 64.0)


def compare_phash(source: MatLike, capture: MatLike, mask: MatLike | None = None):
    """
    Compares the Perceptual Hash of the two given images and returns the similarity between the two.

    @param source: Image of any given shape as a numpy array
    @param capture: Image of any given shape as a numpy array
    @param mask: An image matching the dimensions of the source, but 1 channel grayscale
    @return: The similarity between the hashes of the image as a number 0 to 1.
    """
    # Apply the mask to the source and capture before calculating the
    # pHash for each of the images. As a result of this, this function
    # is not going to be very helpful for large masks as the images
    # when shrunk down to 8x8 will mostly be the same.
    if is_valid_image(mask):
        source = cv2.bitwise_and(source, source, mask=mask)
        capture = cv2.bitwise_and(capture, capture, mask=mask)

    return __cv2_phash(source, capture)


def extract_and_compare_text(capture: MatLike, texts: Iterable[str], methods_index: Iterable[int]):
    """
    Compares the extracted text of the given image and returns the similarity between the two texts.
    The best match of all texts and methods is returned.

    @param capture: Image of any given shape as a numpy array
    @param texts: a list of strings to match for
    @param methods_index: a list of comparison methods to use in order
    @return: The similarity between the text in the image and the text supplied as a number 0 to 1.
    """
    methods = [get_ocr_comparison_method_by_index(i) for i in methods_index]
    png = np.array(cv2.imencode(".png", capture)[1]).tobytes()
    # Especially with stylised characters, OCR could conceivably get the right
    # letter, but mix up the casing (m/M, o/O, t/T, etc.)
    image_string = run_tesseract(png).lower().strip()

    ratio = 0.0
    for text in texts:
        for method in methods:
            ratio = max(ratio, method(text, image_string))
            if ratio == MAX_VALUE:
                return ratio  # we found the best match; try to return early
    return ratio


def compare_submatch(a: str, b: str):
    return float(a in b)


def __compare_dummy(*_: object):
    return 0.0


def get_ocr_comparison_method_by_index(comparison_method_index: int):
    match comparison_method_index:
        case 0:
            return Levenshtein.ratio
        case 1:
            return compare_submatch
        case _:
            return __compare_dummy


def get_comparison_method_by_index(comparison_method_index: int):
    match comparison_method_index:
        case 0:
            return compare_l2_norm
        case 1:
            return compare_histograms
        case 2:
            return compare_phash
        case _:
            return __compare_dummy


def check_if_image_has_transparency(image: MatLike):
    # Check if there's a transparency channel (4th channel)
    # and if at least one pixel is transparent (< 255)
    if image.shape[ImageShape.Channels] != BGRA_CHANNEL_COUNT:
        return False
    mean: float = image[:, :, ColorChannel.Alpha].mean()
    if mean == 0:
        # Non-transparent images code path is usually faster and simpler, so let's return that
        return False
        # TODO: error message if all pixels are transparent
        # (the image appears as all black in windows,
        # so it's not obvious for the user what they did wrong)

    return mean != MAXBYTE
