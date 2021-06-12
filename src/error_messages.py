# Error messages
from PyQt4 import QtGui


def splitImageDirectoryError(self):
    msgBox = QtGui.QMessageBox()
    msgBox.setWindowTitle('Error')
    msgBox.setText("No split image folder is selected.")
    msgBox.exec_()


def splitImageDirectoryNotFoundError(self):
    msgBox = QtGui.QMessageBox()
    msgBox.setWindowTitle('Error')
    msgBox.setText("The Split Image Folder does not exist.")
    msgBox.exec_()


def imageTypeError(self, image):
    msgBox = QtGui.QMessageBox()
    msgBox.setWindowTitle('Error')
    msgBox.setText(
        '"' + image + '" is not a valid image file or the full image file path contains a special character.')
    msgBox.exec_()


def regionError(self):
    msgBox = QtGui.QMessageBox()
    msgBox.setWindowTitle('Error')
    msgBox.setText("No region is selected or the Capture Region window is not open. Select a region or load settings while the Capture Region window is open.")
    msgBox.exec_()


def regionSizeError(self):
    msgBox = QtGui.QMessageBox()
    msgBox.setWindowTitle('Error')
    msgBox.setText("Width and height cannot be 0. Please select a larger region.")
    msgBox.exec_()


def splitHotkeyError(self):
    msgBox = QtGui.QMessageBox()
    msgBox.setWindowTitle('Error')
    msgBox.setText("No split hotkey has been set.")
    msgBox.exec_()


def pauseHotkeyError(self):
    msgBox = QtGui.QMessageBox()
    msgBox.setWindowTitle('Error')
    msgBox.setText("Your split image folder contains an image filename with a pause flag {p}, but no pause hotkey is set.")
    msgBox.exec_()


def customThresholdError(self, image):
    msgBox = QtGui.QMessageBox()
    msgBox.setWindowTitle('Error')
    msgBox.setText("\"" + image + "\" doesn't have a valid custom threshold.")
    msgBox.exec_()


def customPauseError(self, image):
    msgBox = QtGui.QMessageBox()
    msgBox.setWindowTitle('Error')
    msgBox.setText("\"" + image + "\" doesn't have a valid custom pause time.")
    msgBox.exec_()


def alignRegionImageTypeError(self):
    msgBox = QtGui.QMessageBox()
    msgBox.setWindowTitle('Error')
    msgBox.setText("File not a valid image file")
    msgBox.exec_()


def alignmentNotMatchedError(self):
    msgBox = QtGui.QMessageBox()
    msgBox.setWindowTitle('Error')
    msgBox.setText("No area in capture region matched reference image. Alignment failed.")
    msgBox.exec_()


def multipleResetImagesError(self):
    msgBox = QtGui.QMessageBox()
    msgBox.setWindowTitle('Error')
    msgBox.setText("Only one image with the keyword \"reset\" is allowed.")
    msgBox.exec_()


def noResetImageThresholdError(self):
    msgBox = QtGui.QMessageBox()
    msgBox.setWindowTitle('Error')
    msgBox.setText("Reset Image must have a custom threshold. Please set one and check that it is valid")
    msgBox.exec_()


def resetHotkeyError(self):
    msgBox = QtGui.QMessageBox()
    msgBox.setWindowTitle('Error')
    msgBox.setText("Your split image folder contains a reset image, but no reset hotkey is set.")
    msgBox.exec_()


def dummySplitsError(self):
    msgBox = QtGui.QMessageBox()
    msgBox.setWindowTitle('Error')
    msgBox.setText(
        "Group dummy splits when undoing/skipping cannot be checked if any split image has a loop parameter greater than 1")
    msgBox.exec_()


def settingsNotFoundError(self):
    msgBox = QtGui.QMessageBox()
    msgBox.setWindowTitle('Error')
    msgBox.setText("No settings file found. The settings file is saved when the program is closed.")
    msgBox.exec_()


def oldVersionSettingsFileError(self):
    msgBox = QtGui.QMessageBox()
    msgBox.setWindowTitle('Error')
    msgBox.setText("Old version settings file detected. This version allows settings files from v1.3 and above.")
    msgBox.exec_()


def invalidSettingsError(self):
    msgBox = QtGui.QMessageBox()
    msgBox.setWindowTitle('Error')
    msgBox.setText("Invalid settings file.")
    msgBox.exec_()


def noSettingsFileOnOpenError(self):
    msgBox = QtGui.QMessageBox()
    msgBox.setWindowTitle('Error')
    msgBox.setText("No settings file found. One can be loaded on open if placed in the same folder as AutoSplit.exe")
    msgBox.exec_()


def tooManySettingsFilesOnOpenError(self):
    msgBox = QtGui.QMessageBox()
    msgBox.setWindowTitle('Error')
    msgBox.setText("Too many settings files found. Only one can be loaded on open if placed in the same folder as AutoSplit.exe")
    msgBox.exec_()
