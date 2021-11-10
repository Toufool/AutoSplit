# Error messages
from PyQt6 import QtWidgets


def setTextMessage(message: str):
    msgBox = QtWidgets.QMessageBox()
    msgBox.setWindowTitle('Error')
    msgBox.setText(message)
    msgBox.exec()


def splitImageDirectoryError():
    setTextMessage("No split image folder is selected.")


def splitImageDirectoryNotFoundError():
    setTextMessage("The Split Image Folder does not exist.")


def imageTypeError(image):
    setTextMessage('"' + image + '" is not a valid image file or the full image file path contains a special character.')


def regionError():
    setTextMessage("No region is selected or the Capture Region window is not open. Select a region or load settings while the Capture Region window is open.")


def regionSizeError():
    setTextMessage("Width and height cannot be 0. Please select a larger region.")


def splitHotkeyError():
    setTextMessage("No split hotkey has been set.")


def pauseHotkeyError():
    setTextMessage("Your split image folder contains an image filename with a pause flag {p}, but no pause hotkey is set.")


def alignRegionImageTypeError():
    setTextMessage("File not a valid image file")


def alignmentNotMatchedError():
    setTextMessage("No area in capture region matched reference image. Alignment failed.")


def multipleResetImagesError():
    setTextMessage("Only one image with the keyword \"reset\" is allowed.")


def resetHotkeyError():
    setTextMessage("Your split image folder contains a reset image, but no reset hotkey is set.")


def dummySplitsError():
    setTextMessage("Group dummy splits when undoing/skipping cannot be checked if any split image has a loop parameter greater than 1")


def oldVersionSettingsFileError():
    setTextMessage("Old version settings file detected. This version allows settings files from v1.3 and above.")


def invalidSettingsError():
    setTextMessage("Invalid settings file.")


def noSettingsFileOnOpenError():
    setTextMessage("No settings file found. One can be loaded on open if placed in the same folder as AutoSplit.exe")


def tooManySettingsFilesOnOpenError():
    setTextMessage("Too many settings files found. Only one can be loaded on open if placed in the same folder as AutoSplit.exe")
