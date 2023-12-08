import os
from typing import TYPE_CHECKING, TypedDict, cast

import toml
from PySide6 import QtCore, QtWidgets

import error_messages
from capture_method import CAPTURE_METHODS, CaptureMethodEnum, Region, change_capture_method
from gen import design
from hotkeys import HOTKEYS, remove_all_hotkeys, set_hotkey
from utils import auto_split_directory

if TYPE_CHECKING:
    from AutoSplit import AutoSplit


class UserProfileDict(TypedDict):
    split_hotkey: str
    reset_hotkey: str
    undo_split_hotkey: str
    skip_split_hotkey: str
    pause_hotkey: str
    screenshot_hotkey: str
    toggle_auto_reset_image_hotkey: str
    fps_limit: int
    live_capture_region: bool
    capture_method: str | CaptureMethodEnum
    capture_device_id: int
    capture_device_name: str
    default_comparison_method: int
    default_similarity_threshold: float
    default_delay_time: int
    default_pause_time: float
    loop_splits: bool
    start_also_resets: bool
    enable_auto_reset: bool
    split_image_directory: str
    screenshot_directory: str
    open_screenshot: bool
    captured_window_title: str
    capture_region: Region


DEFAULT_PROFILE = UserProfileDict(
    split_hotkey="",
    reset_hotkey="",
    undo_split_hotkey="",
    skip_split_hotkey="",
    pause_hotkey="",
    screenshot_hotkey="",
    toggle_auto_reset_image_hotkey="",
    fps_limit=60,
    live_capture_region=True,
    capture_method=CAPTURE_METHODS.get_method_by_index(0),
    capture_device_id=0,
    capture_device_name="",
    default_comparison_method=0,
    default_similarity_threshold=0.95,
    default_delay_time=0,
    default_pause_time=10,
    loop_splits=False,
    start_also_resets=False,
    enable_auto_reset=True,
    split_image_directory="",
    screenshot_directory="",
    open_screenshot=True,
    captured_window_title="",
    capture_region=Region(x=0, y=0, width=1, height=1),
)


def have_settings_changed(autosplit: "AutoSplit"):
    return (
        autosplit.settings_dict != autosplit.last_saved_settings
        or autosplit.settings_dict != autosplit.last_loaded_settings
    )


def save_settings(autosplit: "AutoSplit"):
    """@return: The save settings filepath. Or None if "Save Settings As" is cancelled."""
    return (
        __save_settings_to_file(autosplit, autosplit.last_successfully_loaded_settings_file_path)
        if autosplit.last_successfully_loaded_settings_file_path
        else save_settings_as(autosplit)
    )


def save_settings_as(autosplit: "AutoSplit"):
    """@return: The save settings filepath selected. Empty if cancelled."""
    # User picks save destination
    save_settings_file_path = QtWidgets.QFileDialog.getSaveFileName(
        autosplit,
        "Save Settings As",
        autosplit.last_successfully_loaded_settings_file_path
        or os.path.join(auto_split_directory, "settings.toml"),
        "TOML (*.toml)",
    )[0]
    # If user cancels save destination window, don't save settings
    if not save_settings_file_path:
        return ""

    return __save_settings_to_file(autosplit, save_settings_file_path)


def __save_settings_to_file(autosplit: "AutoSplit", save_settings_file_path: str):
    autosplit.last_saved_settings = autosplit.settings_dict
    # Save settings to a .toml file
    with open(save_settings_file_path, "w", encoding="utf-8") as file:
        toml.dump(autosplit.last_saved_settings, file)
    autosplit.last_successfully_loaded_settings_file_path = save_settings_file_path
    return save_settings_file_path


def __load_settings_from_file(autosplit: "AutoSplit", load_settings_file_path: str):
    if load_settings_file_path.endswith(".pkl"):
        autosplit.show_error_signal.emit(error_messages.old_version_settings_file)
        return False
    try:
        with open(load_settings_file_path, encoding="utf-8") as file:
            # Casting here just so we can build an actual UserProfileDict once we're done validating
            # Fallback to default settings if some are missing from the file. This happens when new settings are added.
            loaded_settings = DEFAULT_PROFILE | cast(UserProfileDict, toml.load(file))
        # TODO: Data Validation / fallbacks ?
        autosplit.settings_dict = UserProfileDict(**loaded_settings)
        autosplit.last_loaded_settings = autosplit.settings_dict

        autosplit.x_spinbox.setValue(autosplit.settings_dict["capture_region"]["x"])
        autosplit.y_spinbox.setValue(autosplit.settings_dict["capture_region"]["y"])
        autosplit.width_spinbox.setValue(autosplit.settings_dict["capture_region"]["width"])
        autosplit.height_spinbox.setValue(autosplit.settings_dict["capture_region"]["height"])
        autosplit.split_image_folder_input.setText(autosplit.settings_dict["split_image_directory"])
    except (FileNotFoundError, MemoryError, TypeError, toml.TomlDecodeError):
        autosplit.show_error_signal.emit(error_messages.invalid_settings)
        return False

    remove_all_hotkeys()
    if not autosplit.is_auto_controlled:
        for hotkey, hotkey_name in [(hotkey, f"{hotkey}_hotkey") for hotkey in HOTKEYS]:
            hotkey_value = autosplit.settings_dict.get(hotkey_name)
            if hotkey_value:
                set_hotkey(autosplit, hotkey, hotkey_value)

    change_capture_method(cast(CaptureMethodEnum, autosplit.settings_dict["capture_method"]), autosplit)
    if autosplit.settings_dict["capture_method"] != CaptureMethodEnum.VIDEO_CAPTURE_DEVICE:
        autosplit.capture_method.recover_window(autosplit.settings_dict["captured_window_title"])
    if not autosplit.capture_method.check_selected_region_exists():
        autosplit.live_image.setText(
            "Reload settings after opening"
            + f"\n{autosplit.settings_dict['captured_window_title']!r}"
            + "\nto automatically load Capture Region",
        )

    return True


def load_settings(autosplit: "AutoSplit", from_path: str = ""):
    load_settings_file_path = (
        from_path
        or QtWidgets.QFileDialog.getOpenFileName(
            autosplit,
            "Load Profile",
            os.path.join(auto_split_directory, "settings.toml"),
            "TOML (*.toml)",
        )[0]
    )
    if not (load_settings_file_path and __load_settings_from_file(autosplit, load_settings_file_path)):
        return

    autosplit.last_successfully_loaded_settings_file_path = load_settings_file_path
    # TODO: Should this check be in `__load_start_image` ?
    if not autosplit.is_running:
        autosplit.load_start_image_signal.emit(False, True)


def load_settings_on_open(autosplit: "AutoSplit"):
    settings_files = [
        file for file
        in os.listdir(auto_split_directory)
        if file.endswith(".toml")
    ]

    # Find all .tomls in AutoSplit folder, error if there is not exactly 1
    error = None
    if len(settings_files) < 1:
        error = error_messages.no_settings_file_on_open
    elif len(settings_files) > 1:
        error = error_messages.too_many_settings_files_on_open
    if error:
        change_capture_method(CAPTURE_METHODS.get_method_by_index(0), autosplit)
        error()
        return

    load_settings(autosplit, os.path.join(auto_split_directory, settings_files[0]))


def load_check_for_updates_on_open(autosplit: "AutoSplit"):
    """
    Retrieve the "Check For Updates On Open" QSettings and set the checkbox state
    These are only global settings values. They are not *toml settings values.
    """
    # Type not infered by PySide6: https://bugreports.qt.io/browse/PYSIDE-2542
    value = cast(
        bool,
        QtCore
        .QSettings("AutoSplit", "Check For Updates On Open")
        .value("check_for_updates_on_open", True, type=bool),
    )
    autosplit.action_check_for_updates_on_open.setChecked(value)


def set_check_for_updates_on_open(design_window: design.Ui_MainWindow, value: bool):
    """Sets the "Check For Updates On Open" QSettings value and the checkbox state."""
    design_window.action_check_for_updates_on_open.setChecked(value)
    QtCore \
        .QSettings("AutoSplit", "Check For Updates On Open") \
        .setValue("check_for_updates_on_open", value)
