from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from AutoSplit import AutoSplit

import os

import requests
from simplejson.errors import JSONDecodeError
from packaging import version
from PyQt6 import QtWidgets
from PyQt6.QtCore import QThread
from requests.exceptions import RequestException

import error_messages
import settings_file as settings
from gen import about, design, resources_rc, update_checker  # noqa: F401

# AutoSplit Version number
VERSION = "1.6.1"


# About Window
class __AboutWidget(QtWidgets.QWidget, about.Ui_AboutAutoSplitWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.created_by_label.setOpenExternalLinks(True)
        self.donate_button_label.setOpenExternalLinks(True)
        self.version_label.setText(f"Version: {VERSION}")
        self.show()


def open_about(autosplit: AutoSplit):
    autosplit.AboutWidget = __AboutWidget()


class __UpdateCheckerWidget(QtWidgets.QWidget, update_checker.Ui_UpdateChecker):
    def __init__(self, latest_version: str, design_window: design.Ui_MainWindow, check_on_open: bool = False):
        super().__init__()
        self.setupUi(self)
        self.current_version_number_label.setText(VERSION)
        self.latest_version_number_label.setText(latest_version)
        self.left_button.clicked.connect(self.open_update)
        self.do_not_ask_again_checkbox.stateChanged.connect(self.do_not_ask_me_again_state_changed)
        self.design_window = design_window
        if version.parse(latest_version) > version.parse(VERSION):
            self.do_not_ask_again_checkbox.setVisible(check_on_open)
            self.show()
        elif not check_on_open:
            self.update_status_label.setText("You are on the latest AutoSplit version.")
            self.go_to_download_label.setVisible(False)
            self.left_button.setVisible(False)
            self.right_button.setText("OK")
            self.do_not_ask_again_checkbox.setVisible(False)
            self.show()

    def open_update(self):
        os.system('start "" https://github.com/Toufool/Auto-Split/releases/latest')
        self.close()

    def do_not_ask_me_again_state_changed(self):
        settings.set_check_for_updates_on_open(
            self.design_window,
            self.do_not_ask_again_checkbox.isChecked())


def open_update_checker(autosplit: AutoSplit, latest_version: str, check_on_open: bool):
    autosplit.UpdateCheckerWidget = __UpdateCheckerWidget(latest_version, autosplit, check_on_open)


def view_help():
    os.system('start "" https://github.com/Toufool/Auto-Split#tutorial')


class __CheckForUpdatesThread(QThread):
    def __init__(self, autosplit: AutoSplit, check_on_open: bool):
        super().__init__()
        self.autosplit = autosplit
        self.check_on_open = check_on_open

    def run(self):
        try:
            response = requests.get("https://api.github.com/repos/Toufool/Auto-Split/releases/latest")
            latest_version = response.json()["name"].split("v")[1]
            self.autosplit.update_checker_widget_signal.emit(latest_version, self.check_on_open)
        except (RequestException, KeyError, JSONDecodeError):
            if not self.check_on_open:
                self.autosplit.show_error_signal.emit(error_messages.check_for_updates)


def check_for_updates(autosplit: AutoSplit, check_on_open: bool = False):
    autosplit.CheckForUpdatesThread = __CheckForUpdatesThread(autosplit, check_on_open)
    autosplit.CheckForUpdatesThread.start()
