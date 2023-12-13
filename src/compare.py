from math import sqrt
from typing import cast

import cv2
import numpy as np
import numpy._typing as npt
import scipy.fft
from cv2.typing import MatLike

from utils import BGRA_CHANNEL_COUNT, MAXBYTE, ColorChannel, ImageShape, is_valid_image

MAXRANGE = MAXBYTE + 1
CHANNELS = [ColorChannel.Red.value, ColorChannel.Green.value, ColorChannel.Blue.value]
HISTOGRAM_SIZE = [8, 8, 8]
RANGES = [0, MAXRANGE, 0, MAXRANGE, 0, MAXRANGE]
MASK_SIZE_MULTIPLIER = ColorChannel.Alpha * MAXBYTE * MAXBYTE


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
        source.size * MAXBYTE * MAXBYTE
        if not is_valid_image(mask)
        else cv2.countNonZero(mask)
    )

    return 1 - (min_val / max_error)


def __cv2_phash(image: MatLike, hash_size: int = 8, highfreq_factor: int = 4):
    """Implementation copied from https://github.com/JohannesBuchner/imagehash/blob/38005924fe9be17cfed145bbc6d83b09ef8be025/imagehash/__init__.py#L260 ."""  # noqa: E501
    # OpenCV has its own pHash comparison implementation in `cv2.img_hash`, but it requires contrib/extra modules
    # and is innacurate unless we precompute the size with a specific interpolation.
    # See: https://github.com/opencv/opencv_contrib/issues/3295#issuecomment-1172878684
    #
    # pHash = cv2.img_hash.PHash.create()
    # source = cv2.resize(source, (8, 8), interpolation=cv2.INTER_AREA)
    # capture = cv2.resize(capture, (8, 8), interpolation=cv2.INTER_AREA)
    # source_hash = pHash.compute(source)
    # capture_hash = pHash.compute(capture)
    # hash_diff = pHash.compare(source_hash, capture_hash)

    img_size = hash_size * highfreq_factor
    image = cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)
    image = cv2.resize(image, (img_size, img_size), interpolation=cv2.INTER_AREA)
    dct = cast(npt.NDArray[np.float64], scipy.fft.dct(scipy.fft.dct(image, axis=0), axis=1))
    dct_low_frequency = dct[:hash_size, :hash_size]
    median = np.median(dct_low_frequency)
    return dct_low_frequency > median


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
    # when shrinked down to 8x8 will mostly be the same.
    if is_valid_image(mask):
        source = cv2.bitwise_and(source, source, mask=mask)
        capture = cv2.bitwise_and(capture, capture, mask=mask)

    source_hash = __cv2_phash(source)
    capture_hash = __cv2_phash(capture)
    hash_diff = np.count_nonzero(source_hash != capture_hash)

    return 1 - (hash_diff / 64.0)


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


def __compare_dummy(*_: object):
    return 0.0


def check_if_image_has_transparency(image: MatLike):
    # Check if there's a transparency channel (4th channel) and if at least one pixel is transparent (< 255)
    if image.shape[ImageShape.Channels] != BGRA_CHANNEL_COUNT:
        return False
    mean: float = image[:, :, ColorChannel.Alpha].mean()
    if mean == 0:
        # Non-transparent images code path is usually faster and simpler, so let's return that
        return False
        # TODO: error message if all pixels are transparent
        # (the image appears as all black in windows, so it's not obvious for the user what they did wrong)

    return mean != MAXBYTE
