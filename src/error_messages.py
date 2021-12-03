# Error messages
import traceback
from PyQt6 import QtCore, QtWidgets


def setTextMessage(message: str, details: str = ""):
    messageBox = QtWidgets.QMessageBox()
    messageBox.setWindowTitle("Error")
    messageBox.setTextFormat(QtCore.Qt.TextFormat.RichText)
    messageBox.setText(message)
    if details:
        messageBox.setDetailedText(details)
        for button in messageBox.buttons():
            if messageBox.buttonRole(button) == QtWidgets.QMessageBox.ButtonRole.ActionRole:
                button.click()
                break
    messageBox.exec()


def splitImageDirectoryError():
    setTextMessage("No split image folder is selected.")


def splitImageDirectoryNotFoundError():
    setTextMessage("The Split Image Folder does not exist.")


def splitImageDirectoryEmpty():
    setTextMessage("The Split Image Folder is empty.")


def imageTypeError(image: str):
    setTextMessage(f'"{image}" is not a valid image file, does not exist, '
                   "or the full image file path contains a special character.")


def regionError():
    setTextMessage("No region is selected or the Capture Region window is not open. "
                   "Select a region or load settings while the Capture Region window is open.")


def splitHotkeyError():
    setTextMessage("No split hotkey has been set.")


def pauseHotkeyError():
    setTextMessage("Your split image folder contains an image filename with a pause flag {p}, "
                   "but no pause hotkey is set.")


def alignRegionImageTypeError():
    setTextMessage("File not a valid image file")


def alignmentNotMatchedError():
    setTextMessage("No area in capture region matched reference image. Alignment failed.")


def noKeywordImageError(keyword: str):
    setTextMessage(f'Your split image folder does not contain an image with the keyword "{keyword}".')


def multipleKeywordImagesError(keyword: str):
    setTextMessage(f'Only one image with the keyword "{keyword}" is allowed.')


def resetHotkeyError():
    setTextMessage("Your split image folder contains a reset image, but no reset hotkey is set.")


def dummySplitsError():
    setTextMessage("Group dummy splits when undoing/skipping cannot be checked "
                   "if any split image has a loop parameter greater than 1")


def oldVersionSettingsFileError():
    setTextMessage("Old version settings file detected. This version allows settings files from v1.3 and above.")


def invalidSettingsError():
    setTextMessage("Invalid settings file.")


def noSettingsFileOnOpenError():
    setTextMessage("No settings file found. One can be loaded on open if placed in the same folder as AutoSplit.exe")


def tooManySettingsFilesOnOpenError():
    setTextMessage("Too many settings files found. "
                   "Only one can be loaded on open if placed in the same folder as AutoSplit.exe")


def checkForUpdatesError():
    setTextMessage("An error occurred while attempting to check for updates. Please check your connection.")


def loadStartImageError():
    setTextMessage("Start Image found, but cannot be loaded unless Start, Reset, and Pause hotkeys are set. "
                   "Please set these hotkeys, and then click the Reload Start Image button.")


def stdinLostError():
    setTextMessage("stdin not supported or lost, external control like LiveSplit integration will not work.")


def exceptionTraceback(message: str, exception: BaseException):
    setTextMessage(
        message,
        "\n".join(traceback.format_exception(None, exception, exception.__traceback__)))
