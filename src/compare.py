from PIL import Image
import imagehash

import numpy as np
import cv2

def compare_histograms(source, capture):
    """
    Compares two images by calculating their histograms, normalizing them, and
    then comparing them using Bhattacharyya distance.

    @param source: 3 color image of any given width and height
    @param capture: An image matching the dimensions of the source
    @return: The similarity between the histograms as a number 0 to 1.
    """

    source_hist = cv2.calcHist([source], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
    capture_hist = cv2.calcHist([capture], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])

    cv2.normalize(source_hist, source_hist)
    cv2.normalize(capture_hist, capture_hist)

    return 1 - cv2.compareHist(source_hist, capture_hist, cv2.HISTCMP_BHATTACHARYYA)

def compare_histograms_masked(source, capture, mask):
    """
    Compares two images by calculating their histograms using a mask, normalizing
    them, and then comparing them using Bhattacharyya distance.

    @param source: 3 color image of any given width and height
    @param capture: An image matching the dimensions of the source
    @param mask: An image matching the dimensions of the source, but 1 channel grayscale
    @return: The similarity between the histograms as a number 0 to 1.
    """
    source_hist = cv2.calcHist([source], [0, 1, 2], mask, [8, 8, 8], [0, 256, 0, 256, 0, 256])
    capture_hist = cv2.calcHist([capture], [0, 1, 2], mask, [8, 8, 8], [0, 256, 0, 256, 0, 256])

    cv2.normalize(source_hist, source_hist)
    cv2.normalize(capture_hist, capture_hist)

    return 1 - cv2.compareHist(source_hist, capture_hist, cv2.HISTCMP_BHATTACHARYYA)

def compare_l2_norm(source, capture):
    """
    Compares two images by calculating the L2 Error (square-root
    of sum of squared error)

    @param source: Image of any given shape
    @param capture: Image matching the dimensions of the source
    @return: The similarity between the images as a number 0 to 1.
    """

    error = cv2.norm(source, capture, cv2.NORM_L2)

    # The L2 Error is summed across all pixels, so this normalizes
    max_error = (source.size ** 0.5) * 255

    return 1 - (error/max_error)

def compare_l2_norm_masked(source, capture, mask):
    """
    Compares two images by calculating the L2 Error (square-root
    of sum of squared error)

    @param source: Image of any given shape
    @param capture: Image matching the dimensions of the source
    @param mask: An image matching the dimensions of the source, but 1 channel grayscale
    @return: The similarity between the images as a number 0 to 1.
    """

    error = cv2.norm(source, capture, cv2.NORM_L2, mask)

    # The L2 Error is summed across all pixels, so this normalizes
    max_error = (3 * np.count_nonzero(mask) * 255 * 255) ** 0.5

    return 1 - (error / max_error)

def compare_template(source, capture):
    """
    Checks if the source is located within the capture by using
    the sum of square differences.

    @param source: The subsection being searched for within the capture
    @param capture: Capture of an image larger than the source
    @return: The best similarity for a region found in the image. This is
    represented as a number from 0 to 1.
    """

    result = cv2.matchTemplate(capture, source, cv2.TM_SQDIFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    # matchTemplate returns the sum of square differences, this is the max
    # that the value can be. Used for normalizing from 0 to 1.
    max_error = source.size * 255 * 255

    return 1 - (min_val/max_error)

def compare_template_masked(source, capture, mask):
    """
    Checks if the source is located within the capture by using
    the sum of square differences. The mask is used to search for
    non-rectangular images within the capture

    @param source: The subsection being searched for within the capture
    @param capture: Capture of an image larger than the source
    @param mask: The mask of the source with the same dimensions
    @return: The best similarity for a region found in the image. This is
    represented as a number from 0 to 1.
    """

    result = cv2.matchTemplate(capture, source, cv2.TM_SQDIFF, None, mask)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    return 1 - (min_val/np.count_nonzero(mask))

def compare_phash(source, capture):
    """
    Compares the pHash of the two given images and returns the similarity between
    the two.

    @param source: Image of any given shape as a numpy array
    @param capture: Image of any given shape as a numpy array
    @return: The similarity between the hashes of the image as a number 0 to 1.
    """

    source = Image.fromarray(source)
    capture = Image.fromarray(capture)

    source_hash = imagehash.phash(source)
    capture_hash = imagehash.phash(capture)

    return 1 - ((source_hash - capture_hash)/64.0)

def compare_phash_masked(source, capture, mask):
    """
    Compares the pHash of the two given images and returns the similarity between
    the two.

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
    source = cv2.bitwise_and(source, source, mask=mask)
    capture = cv2.bitwise_and(capture, capture, mask=mask)

    source = Image.fromarray(source)
    capture = Image.fromarray(capture)

    source_hash = imagehash.phash(source)
    capture_hash = imagehash.phash(capture)

    return 1 - ((source_hash - capture_hash)/64.0)


def checkIfImageHasTransparency(self):
    source = cv2.imread(self.split_image_path, cv2.IMREAD_UNCHANGED)
    # Check if there's a transparency channel (4th channel) and if at least one pixel is transparent (< 255)
    return source.shape[2] == 4 and np.mean(source[:, :, 3]) != 255
