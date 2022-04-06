from __future__ import annotations
from typing import Optional
from PIL import Image
from win32con import MAXBYTE
import cv2
import imagehash  # https://github.com/JohannesBuchner/imagehash/issues/151
import numpy as np

MAXRANGE = MAXBYTE + 1
channels = [0, 1, 2]
histogram_size = [8, 8, 8]
ranges = [0, MAXRANGE, 0, MAXRANGE, 0, MAXRANGE]


def compare_histograms(source: cv2.ndarray, capture: cv2.ndarray, mask: Optional[cv2.ndarray] = None):
    """
    Compares two images by calculating their histograms, normalizing
    them, and then comparing them using Bhattacharyya distance.

    @param source: 3 color image of any given width and height
    @param capture: An image matching the dimensions of the source
    @param mask: An image matching the dimensions of the source, but 1 channel grayscale
    @return: The similarity between the histograms as a number 0 to 1.
    """

    source_hist = cv2.calcHist([source], channels, mask, histogram_size, ranges)
    capture_hist = cv2.calcHist([capture], channels, mask, histogram_size, ranges)

    cv2.normalize(source_hist, source_hist)
    cv2.normalize(capture_hist, capture_hist)

    return 1 - cv2.compareHist(source_hist, capture_hist, cv2.HISTCMP_BHATTACHARYYA)


def compare_l2_norm(source: cv2.ndarray, capture: cv2.ndarray, mask: Optional[cv2.ndarray] = None):
    """
    Compares two images by calculating the L2 Error (square-root of sum of squared error)
    @param source: Image of any given shape
    @param capture: Image matching the dimensions of the source
    @param mask: An image matching the dimensions of the source, but 1 channel grayscale
    @return: The similarity between the images as a number 0 to 1.
    """

    # https://github.com/microsoft/pylance-release/issues/2089
    error = cv2.norm(source, capture, cv2.NORM_L2, mask)  # type: ignore

    # The L2 Error is summed across all pixels, so this normalizes
    max_error = (source.size ** 0.5) * MAXBYTE \
        if mask is None \
        else (3 * np.count_nonzero(mask) * MAXBYTE * MAXBYTE) ** 0.5

    if not max_error:
        return 0.0
    return 1 - (error / max_error)


def compare_template(source: cv2.ndarray, capture: cv2.ndarray, mask: Optional[cv2.ndarray] = None):
    """
    Checks if the source is located within the capture by using the sum of square differences.
    The mask is used to search for non-rectangular images within the capture

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
    max_error = source.size * MAXBYTE * MAXBYTE \
        if mask is None \
        else np.count_nonzero(mask)

    return 1 - (min_val / max_error)


def compare_phash(source: cv2.ndarray, capture: cv2.ndarray, mask: Optional[cv2.ndarray] = None):
    """
    Compares the Perceptual Hash of the two given images and returns the similarity between the two.

    @param source: Image of any given shape as a numpy array
    @param capture: Image of any given shape as a numpy array
    @param mask: An image matching the dimensions of the source, but 1 channel grayscale
    @return: The similarity between the hashes of the image as a number 0 to 1.
    """

    # Since imagehash doesn't have any masking itself, bitwise_and will allow us
    # to apply the mask to the source and capture before calculating the pHash for
    # each of the images. As a result of this, this function is not going to be very
    # helpful for large masks as the images when shrinked down to 8x8 will mostly be
    # the same
    if mask is not None:
        source = cv2.bitwise_and(source, source, mask=mask)
        capture = cv2.bitwise_and(capture, capture, mask=mask)

    source_hash = imagehash.phash(Image.fromarray(source))
    capture_hash = imagehash.phash(Image.fromarray(capture))
    hash_diff = source_hash - capture_hash
    if not hash_diff:
        return 0.0
    return 1 - (hash_diff / 64.0)


def check_if_image_has_transparency(image: cv2.ndarray):
    # Check if there's a transparency channel (4th channel) and if at least one pixel is transparent (< 255)
    if image.shape[2] != 4:
        return False
    mean: float = np.mean(image[:, :, 3])
    if mean == 0:
        # Non-transparent images code path is usually faster and simpler, so let's return that
        return False
        # TODO error message if all pixels are transparent
        # (the image appears as all black in windows, so it's not obvious for the user what they did wrong)

    return mean != 255
