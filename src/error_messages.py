# Error messages
from PyQt6 import QtWidgets


def setTextMessage(message: str):
    msgBox = QtWidgets.QMessageBox()
    msgBox.setWindowTitle('Error')
    msgBox.setText(message)
    msgBox.exec()


def splitImageDirectoryError(self):
    setTextMessage("No split image folder is selected.")


def splitImageDirectoryNotFoundError(self):
    setTextMessage("The Split Image Folder does not exist.")


def imageTypeError(self, image):
    setTextMessage('"' + image + '" is not a valid image file or the full image file path contains a special character.')


def regionError(self):
    setTextMessage("No region is selected or the Capture Region window is not open. Select a region or load settings while the Capture Region window is open.")


def regionSizeError(self):
    setTextMessage("Width and height cannot be 0. Please select a larger region.")


def splitHotkeyError(self):
    setTextMessage("No split hotkey has been set.")


def pauseHotkeyError(self):
    setTextMessage("Your split image folder contains an image filename with a pause flag {p}, but no pause hotkey is set.")


def alignRegionImageTypeError(self):
    setTextMessage("File not a valid image file")


def alignmentNotMatchedError(self):
    setTextMessage("No area in capture region matched reference image. Alignment failed.")


def multipleResetImagesError(self):
    setTextMessage("Only one image with the keyword \"reset\" is allowed.")


def resetHotkeyError(self):
    setTextMessage("Your split image folder contains a reset image, but no reset hotkey is set.")


def dummySplitsError(self):
    setTextMessage("Group dummy splits when undoing/skipping cannot be checked if any split image has a loop parameter greater than 1")


def oldVersionSettingsFileError(self):
    setTextMessage("Old version settings file detected. This version allows settings files from v1.3 and above.")


def invalidSettingsError(self):
    setTextMessage("Invalid settings file.")


def noSettingsFileOnOpenError(self):
    setTextMessage("No settings file found. One can be loaded on open if placed in the same folder as AutoSplit.exe")


def tooManySettingsFilesOnOpenError(self):
    setTextMessage("Too many settings files found. Only one can be loaded on open if placed in the same folder as AutoSplit.exe")
