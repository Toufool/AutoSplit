from PIL import Image
import imagehash

import numpy as np
import cv2

def compare_histograms(source, capture):
    """
    Compares two images by calculating their histograms, normalizing them, and
    then comparing them using Bhattacharyya distance.

    @param source: 3 color SplitImage of any given width and height
    @param capture: An image matching the dimensions of the source
    @return: The similarity between the histograms as a number 0 to 1
    """

    source_hist = cv2.calcHist([source.image], [0, 1, 2], source.mask, [8, 8, 8], [0, 256, 0, 256, 0, 256])
    capture_hist = cv2.calcHist([capture], [0, 1, 2], source.mask, [8, 8, 8], [0, 256, 0, 256, 0, 256])

    cv2.normalize(source_hist, source_hist)
    cv2.normalize(capture_hist, capture_hist)

    return 1 - cv2.compareHist(source_hist, capture_hist, cv2.HISTCMP_BHATTACHARYYA)

def compare_l2_norm(source, capture):
    """
    Compares two images by calculating the L2 Error (square-root
    of sum of squared error)

    @param source: SplitImage of any given shape
    @param capture: Image matching the dimensions of the source
    @return: The similarity between the images as a number 0 to 1
    """

    if source.mask is None:
        error = cv2.norm(source.image, capture, cv2.NORM_L2)

        # The L2 Error is summed across all pixels, so this normalizes
        max_error = (source.image.size ** 0.5) * 255

    else:
        error = cv2.norm(source.image, capture, cv2.NORM_L2, source.mask)

        # The L2 Error is summed across all pixels, so this normalizes
        max_error = (3 * np.count_nonzero(source.mask) * 255 * 255) ** 0.5

    return 1 - (error / max_error)

def compare_template(source, capture):
    """
    Checks if the source is located within the capture by using
    the sum of square differences.

    @param source: The subsection being searched for within the capture
    @param capture: Capture of an image larger than the source
    @return: The best similarity for a region found in the image. This is
    represented as a number from 0 to 1
    """

    if source.mask is None:
        result = cv2.matchTemplate(capture, source.image, cv2.TM_SQDIFF)
    else:
        result = cv2.matchTemplate(capture, source.image, cv2.TM_SQDIFF, None, source.mask)

    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    if source.mask is None:
        # matchTemplate returns the sum of square differences, this is the max
        # that the value can be. Used for normalizing from 0 to 1.
        max_error = source.size * 255 * 255

        return 1 - (min_val / max_error)
    else:
        return 1 - (min_val / np.count_nonzero(source.mask))

def compare_phash(source, capture):
    """
    Compares the pHash of the two given images and returns the similarity between
    the two.
    
    @param source: SplitImage of any given shape
    @param capture: SplitImage of any given shape
    @return: The similarity between the hashes of the image as a number 0 to 1.
    """

    if source.mask is not None:
        # Since imagehash doesn't have any masking itself, bitwise_and will allow us
        # to apply the mask to the source and capture before calculating the pHash for
        # each of the images. As a result of this, this function is not going to be very
        # helpful for large masks as the images when shrinked down to 8x8 will mostly be
        # the same
        source.image = np.array(source.image)
        capture = np.array(capture)

        source.image = cv2.bitwise_and(source.image, source.image, mask=source.mask)
        capture = cv2.bitwise_and(capture, capture, mask=source.mask)

        source.image = Image.fromarray(source.image)
        capture = Image.fromarray(capture)

    source_hash = imagehash.phash(source.image)
    capture_hash = imagehash.phash(capture)

    return 1 - ((source_hash - capture_hash) / 64.0)
