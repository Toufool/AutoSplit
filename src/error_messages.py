# Error messages
import traceback
from PyQt6 import QtCore, QtWidgets


def set_text_message(message: str, details: str = ""):
    message_box = QtWidgets.QMessageBox()
    message_box.setWindowTitle("Error")
    message_box.setTextFormat(QtCore.Qt.TextFormat.RichText)
    message_box.setText(message)
    if details:
        message_box.setDetailedText(details)
        for button in message_box.buttons():
            if message_box.buttonRole(button) == QtWidgets.QMessageBox.ButtonRole.ActionRole:
                button.click()
                break
    message_box.exec()


def split_image_directory():
    set_text_message("No split image folder is selected.")


def split_image_directory_not_found():
    set_text_message("The Split Image Folder does not exist.")


def split_image_directory_empty():
    set_text_message("The Split Image Folder is empty.")


def image_type(image: str):
    set_text_message(f'"{image}" is not a valid image file, does not exist, '
                     "or the full image file path contains a special character.")


def region():
    set_text_message("No region is selected or the Capture Region window is not open. "
                     "Select a region or load settings while the Capture Region window is open.")


def split_hotkey():
    set_text_message("No split hotkey has been set.")


def pause_hotkey():
    set_text_message("Your split image folder contains an image filename with a pause flag {p}, "
                     "but no pause hotkey is set.")


def align_region_image_type():
    set_text_message("File not a valid image file")


def alignment_not_matched():
    set_text_message("No area in capture region matched reference image. Alignment failed.")


def no_keyword_image(keyword: str):
    set_text_message(f'Your split image folder does not contain an image with the keyword "{keyword}".')


def multiple_keyword_images(keyword: str):
    set_text_message(f'Only one image with the keyword "{keyword}" is allowed.')


def reset_hotkey():
    set_text_message("Your split image folder contains a reset image, but no reset hotkey is set.")


def dummy_splits():
    set_text_message("Group dummy splits when undoing/skipping cannot be checked "
                     "if any split image has a loop parameter greater than 1")


def old_version_settings_file():
    set_text_message("Old version settings file detected. This version allows settings files from v1.3 and above.")


def invalid_settings():
    set_text_message("Invalid settings file.")


def no_settings_file_on_open():
    set_text_message("No settings file found. One can be loaded on open if placed in the same folder as AutoSplit.exe")


def too_many_settings_files_on_open():
    set_text_message("Too many settings files found. "
                     "Only one can be loaded on open if placed in the same folder as AutoSplit.exe")


def check_for_updates():
    set_text_message("An error occurred while attempting to check for updates. Please check your connection.")


def load_start_image():
    set_text_message("Start Image found, but cannot be loaded unless Start, Reset, and Pause hotkeys are set. "
                     "Please set these hotkeys, and then click the Reload Start Image button.")


def stdin_lost():
    set_text_message("stdin not supported or lost, external control like LiveSplit integration will not work.")


def exception_traceback(message: str, exception: BaseException):
    set_text_message(
        message,
        "\n".join(traceback.format_exception(None, exception, exception.__traceback__)))
