import design
import about
import sys
import os
from PyQt4 import QtGui, QtCore, QtTest
import win32con
import win32gui
import win32ui
import cv2
import time
import ctypes.wintypes
import ctypes
import numpy as np
import keyboard
import threading
import pickle


class AutoSplit(QtGui.QMainWindow, design.Ui_MainWindow):
    myappid = u'mycompany.myproduct.subproduct.version'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    # signals
    updateCurrentSplitImage = QtCore.pyqtSignal(QtGui.QImage)
    startAutoSplitterSignal = QtCore.pyqtSignal()
    afterSettingHotkeySignal = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(AutoSplit, self).__init__(parent)
        self.setupUi(self)

        # close all proccesses when closing window
        self.actionView_Help.triggered.connect(self.viewHelp)
        self.actionAbout.triggered.connect(self.about)

        # disable buttons upon open
        self.undosplitButton.setEnabled(False)
        self.skipsplitButton.setEnabled(False)
        self.resetButton.setEnabled(False)

        # set hwnd (the capture region window) to 0 initially to catch if user hasn't set a region yet
        self.hwnd = 0

        # resize to these width and height so that FPS performance increases
        self.RESIZE_WIDTH = 320
        self.RESIZE_HEIGHT = 240

        # split image folder line edit text
        self.splitimagefolderLineEdit.setText('No Folder Selected')

        # Connecting button clicks to functions
        self.browseButton.clicked.connect(self.browse)
        self.selectregionButton.clicked.connect(self.selectRegion)
        self.positionUpButton.clicked.connect(self.positionUp)
        self.positionRightButton.clicked.connect(self.positionRight)
        self.positionDownButton.clicked.connect(self.positionDown)
        self.positionLeftButton.clicked.connect(self.positionLeft)
        self.takescreenshotButton.clicked.connect(self.takeScreenshot)
        self.startautosplitterButton.clicked.connect(self.autoSplitter)
        self.checkfpsButton.clicked.connect(self.checkFPS)
        self.resetButton.clicked.connect(self.reset)
        self.skipsplitButton.clicked.connect(self.skipSplit)
        self.undosplitButton.clicked.connect(self.undoSplit)
        self.setsplithotkeyButton.clicked.connect(self.setSplitHotkey)
        self.setresethotkeyButton.clicked.connect(self.setResetHotkey)
        self.setskipsplithotkeyButton.clicked.connect(self.setSkipSplitHotkey)
        self.setundosplithotkeyButton.clicked.connect(self.setUndoSplitHotkey)

        # update height and width when changing the value of these spinbox's
        self.widthSpinBox.valueChanged.connect(self.updateWidth)
        self.heightSpinBox.valueChanged.connect(self.updateHeight)

        # connect signals to functions
        self.updateCurrentSplitImage.connect(self.updateSplitImage)
        self.startAutoSplitterSignal.connect(self.autoSplitter)
        self.afterSettingHotkeySignal.connect(self.afterSettingHotkey)

        # live image checkbox
        self.liveimageCheckBox.clicked.connect(self.checkLiveImage)
        self.timerLiveImage = QtCore.QTimer()
        self.timerLiveImage.timeout.connect(self.liveImageFunction)

        # try to load settings from when user last closed the window
        try:
            with open('settings.pkl', 'rb') as f:
                self.split_image_directory, self.similarity_threshold, self.pause, self.fps_limit, self.split_key, self.reset_key, self.skip_split_key, self.undo_split_key = pickle.load(
                    f)
            self.split_image_directory = str(self.split_image_directory)
            self.splitimagefolderLineEdit.setText(self.split_image_directory)
            self.similaritythresholdDoubleSpinBox.setValue(self.similarity_threshold)
            self.pauseSpinBox.setValue(self.pause)
            self.fpslimitSpinBox.setValue(self.fps_limit)

            # try to set hotkeys from when user last closed the window
            try:
                self.splitLineEdit.setText(str(self.split_key))
                self.split_hotkey = keyboard.add_hotkey(str(self.split_key), self.startAutoSplitter)
                self.old_split_key = self.split_key
            # pass if the key is an empty string (hotkey was never set)
            except ValueError:
                pass

            try:
                self.resetLineEdit.setText(str(self.reset_key))
                self.reset_hotkey = keyboard.add_hotkey(str(self.reset_key), self.reset)
                self.old_reset_key = self.reset_key
            except ValueError:
                pass

            try:
                self.skipsplitLineEdit.setText(str(self.skip_split_key))
                self.skip_split_hotkey = keyboard.add_hotkey(str(self.skip_split_key), self.skipSplit)
                self.old_skip_split_key = self.skip_split_key
            except ValueError:
                pass

            try:
                self.undosplitLineEdit.setText(str(self.undo_split_key))
                self.undo_split_hotkey = keyboard.add_hotkey(str(self.undo_split_key), self.undoSplit)
                self.old_undo_split_key = self.undo_split_key
            except ValueError:
                pass

        except IOError:
            pass

    # FUNCTIONS

    def viewHelp(self):
        os.system("start \"\" https://github.com/Toufool/Auto-Split#tutorial")
        return

    def about(self):
        self.AboutWidget = AboutWidget()

    def browse(self):
        # User selects the file with the split images in it.
        self.split_image_directory = str(
            QtGui.QFileDialog.getExistingDirectory(self, "Select Split Image Directory")) + '\\'

        # If the user doesn't select a folder, it defaults to \. Set it back to whats in the LineEdit, and return
        if self.split_image_directory == '\\':
            self.split_image_directory = self.splitimagefolderLineEdit.text()
            return

        # set the split image folder line to the directory text
        self.splitimagefolderLineEdit.setText(self.split_image_directory)

    def selectRegion(self):
        # call screen region widget
        self.SelectRegionWidget = SelectRegionWidget()

        # wait until height and width change before we continue the function
        while self.SelectRegionWidget.height == -1 and self.SelectRegionWidget.width == -1:
            QtTest.QTest.qWait(1)

        # return an error if width or height are zero.
        if self.SelectRegionWidget.width == 0 or self.SelectRegionWidget.height == 0:
            self.regionSizeError()
            return

        # change width and height spinbox values
        self.widthSpinBox.setValue(self.SelectRegionWidget.width)
        self.heightSpinBox.setValue(self.SelectRegionWidget.height)

        # update x1,y1,width,height values
        self.x1 = self.SelectRegionWidget.x1
        self.y1 = self.SelectRegionWidget.y1
        self.width = self.SelectRegionWidget.width
        self.height = self.SelectRegionWidget.height

        # update selected window using the top left coordinate of the region that the user selects
        self.hwnd = win32gui.WindowFromPoint((self.x1, self.y1))
        while win32gui.IsChild(win32gui.GetParent(self.hwnd), self.hwnd):
            self.hwnd = ctypes.windll.user32.GetAncestor(self.hwnd, win32con.GA_ROOT)
        DwmGetWindowAttribute = ctypes.windll.dwmapi.DwmGetWindowAttribute
        DWMWA_EXTENDED_FRAME_BOUNDS = 9
        rect = ctypes.wintypes.RECT()
        DwmGetWindowAttribute(self.hwnd,
                              ctypes.wintypes.DWORD(DWMWA_EXTENDED_FRAME_BOUNDS),
                              ctypes.byref(rect),
                              ctypes.sizeof(rect)
                              )

        self.top_old = rect.top - (rect.top - win32gui.GetWindowRect(self.hwnd)[1])
        self.left_old = rect.left - (rect.left - win32gui.GetWindowRect(self.hwnd)[0])

        # check if live image needs to be turned on or just set a single image
        self.checkLiveImage()

    def checkLiveImage(self):
        if self.liveimageCheckBox.isChecked():
            self.timerLiveImage.start(1000 / 60)
        else:
            self.timerLiveImage.stop()
            self.liveImageFunction()

    def liveImageFunction(self):
        try:
            if win32gui.GetWindowText(self.hwnd) == '':
                self.regionError()
                self.timerLiveImage.stop()
                return
            ctypes.windll.user32.SetProcessDPIAware()
            DwmGetWindowAttribute = ctypes.windll.dwmapi.DwmGetWindowAttribute
            DWMWA_EXTENDED_FRAME_BOUNDS = 9
            rect = ctypes.wintypes.RECT()
            DwmGetWindowAttribute(self.hwnd,
                                  ctypes.wintypes.DWORD(DWMWA_EXTENDED_FRAME_BOUNDS),
                                  ctypes.byref(rect),
                                  ctypes.sizeof(rect)
                                  )
            self.top = self.y1 - self.top_old
            self.left = self.x1 - self.left_old

            wDC = win32gui.GetWindowDC(self.hwnd)
            dcObj = win32ui.CreateDCFromHandle(wDC)
            cDC = dcObj.CreateCompatibleDC()
            bmp = win32ui.CreateBitmap()
            bmp.CreateCompatibleBitmap(dcObj, self.width, self.height)
            cDC.SelectObject(bmp)
            cDC.BitBlt((0, 0), (self.width, self.height), dcObj, (self.left, self.top), win32con.SRCCOPY)

            img = bmp.GetBitmapBits(True)
            img = np.frombuffer(img, dtype='uint8')
            img.shape = (self.height, self.width, 4)

            img = cv2.resize(img, (240, 180))  # Resize to match the label size

            img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)

            # Convert to set it on the label
            qImg = QtGui.QImage(img, img.shape[1], img.shape[0], img.shape[1] * 3, QtGui.QImage.Format_RGB888)
            pix = QtGui.QPixmap(qImg)
            self.liveImage.setPixmap(pix)

            # Cleanup
            dcObj.DeleteDC()
            cDC.DeleteDC()
            win32gui.ReleaseDC(self.hwnd, wDC)
            win32gui.DeleteObject(bmp.GetHandle())

        except AttributeError:
            pass

    # position arrow buttons point to these functions
    def positionUp(self):
        try:
            self.y1 = self.y1 - 1
            self.checkLiveImage()
        # pass if no region is selected
        except AttributeError:
            pass

    def positionRight(self):
        try:
            self.x1 = self.x1 + 1
            self.checkLiveImage()
        except AttributeError:
            pass

    def positionDown(self):
        try:
            self.y1 = self.y1 + 1
            self.checkLiveImage()
        except AttributeError:
            pass

    def positionLeft(self):
        try:
            self.x1 = self.x1 - 1
            self.checkLiveImage()
        except AttributeError:
            pass

    # update width or height when changing the value of the spinbox's
    def updateWidth(self):
        self.width = self.widthSpinBox.value()
        self.checkLiveImage()

    def updateHeight(self):
        self.height = self.heightSpinBox.value()
        self.checkLiveImage()

    # update current split image. needed this to avoid updating it through the hotkey thread.
    def updateSplitImage(self, qImg):
        pix = QtGui.QPixmap(qImg)
        self.currentSplitImage.setPixmap(pix)

    def takeScreenshot(self):
        # error checks
        if self.splitimagefolderLineEdit.text() == 'No Folder Selected':
            self.splitImageDirectoryError()
            return
        if self.hwnd == 0 or win32gui.GetWindowText(self.hwnd) == '':
            self.regionError()
            return

        take_screenshot_file = 'split_image'

        # check if file exists and rename it if it does
        i = 1
        while os.path.exists(self.split_image_directory + take_screenshot_file + '.png') == True:
            take_screenshot_file = 'split_image' + ' ' + '(' + str(i) + ')'
            i = i + 1

        # grab screenshot of capture region
        wDC = win32gui.GetWindowDC(self.hwnd)
        dcObj = win32ui.CreateDCFromHandle(wDC)
        cDC = dcObj.CreateCompatibleDC()
        bmp = win32ui.CreateBitmap()
        bmp.CreateCompatibleBitmap(dcObj, self.width, self.height)
        cDC.SelectObject(bmp)
        cDC.BitBlt((0, 0), (self.width, self.height), dcObj, (self.left, self.top), win32con.SRCCOPY)

        sct_img = bmp.GetBitmapBits(True)
        sct_img = np.frombuffer(sct_img, dtype='uint8')
        sct_img.shape = (self.height, self.width, 4)

        # save and open image
        cv2.imwrite(self.split_image_directory + take_screenshot_file + '.png', sct_img)
        os.startfile(self.split_image_directory + take_screenshot_file + '.png')

        # Cleanup
        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, wDC)
        win32gui.DeleteObject(bmp.GetHandle())

    # HOTKEYS. I'll comment on one, and the rest are just variations in variables.
    def setSplitHotkey(self):
        self.setsplithotkeyButton.setText('Press a key..')

        # disable some buttons
        self.beforeSettingHotkey()

        # new thread points to callback. this thread is needed or GUI will freeze
        # while the program waits for user input on the hotkey
        def callback():
            # try to remove the previously set hotkey if there is one.
            try:
                keyboard.remove_hotkey(self.split_hotkey)
            except AttributeError:
                pass

            # wait until user presses the hotkey, then keyboard module reads the inpu
            self.split_key = keyboard.read_hotkey(False)

            # If the key the user presses is equal to itself or another hotkey already set,
            # this causes issues. so here, it catches that, and will make no changes to the hotkey.
            try:
                if self.split_key == self.splitLineEdit.text() or self.split_key == self.resetLineEdit.text() or self.split_key == self.skipsplitLineEdit.text() or self.split_key == self.undosplitLineEdit.text():
                    self.split_hotkey = keyboard.add_hotkey(self.old_split_key, self.startAutoSplitter)
                    self.afterSettingHotkeySignal.emit()
                    return
            except AttributeError:
                self.afterSettingHotkeySignal.emit()
                return

            # keyboard module allows you to hit multiple keys for a hotkey. they are joined
            # together by +. If user hits two keys at the same time, make no changes to the
            # hotkey. A try and except is needed if a hotkey hasn't been set yet.
            try:
                if '+' in self.split_key:
                    self.split_hotkey = keyboard.add_hotkey(self.old_split_key, self.startAutoSplitter)
                    self.afterSettingHotkeySignal.emit()
                    return
            except AttributeError:
                self.afterSettingHotkeySignal.emit()
                return

            # add the key as the hotkey, set the text into the LineEdit, set it as old_xxx_key,
            # then emite a signal to re-enable some buttons and change some text in GUI.
            self.split_hotkey = keyboard.add_hotkey(self.split_key, self.startAutoSplitter)
            self.splitLineEdit.setText(self.split_key)
            self.old_split_key = self.split_key
            self.afterSettingHotkeySignal.emit()
            return

        t = threading.Thread(target=callback)
        t.start()
        return

    def setResetHotkey(self):
        self.setresethotkeyButton.setText('Press a key..')
        self.beforeSettingHotkey()

        def callback():
            try:
                keyboard.remove_hotkey(self.reset_hotkey)
            except AttributeError:
                pass
            self.reset_key = keyboard.read_hotkey(False)
            try:
                if self.reset_key == self.splitLineEdit.text() or self.reset_key == self.resetLineEdit.text() or self.reset_key == self.skipsplitLineEdit.text() or self.reset_key == self.undosplitLineEdit.text():
                    self.reset_hotkey = keyboard.add_hotkey(self.old_reset_key, self.reset)
                    self.afterSettingHotkeySignal.emit()
                    return
            except AttributeError:
                self.afterSettingHotkeySignal.emit()
                return
            try:
                if '+' in self.reset_key:
                    self.reset_hotkey = keyboard.add_hotkey(self.old_reset_key, self.reset)
                    self.afterSettingHotkeySignal.emit()
                    return
            except AttributeError:
                self.afterSettingHotkeySignal.emit()
                return
            self.reset_hotkey = keyboard.add_hotkey(self.reset_key, self.reset)
            self.resetLineEdit.setText(self.reset_key)
            self.old_reset_key = self.reset_key
            self.afterSettingHotkeySignal.emit()
            return

        t = threading.Thread(target=callback)
        t.start()
        return

    def setSkipSplitHotkey(self):
        self.setskipsplithotkeyButton.setText('Press a key..')
        self.beforeSettingHotkey()

        def callback():
            try:
                keyboard.remove_hotkey(self.skip_split_hotkey)
            except AttributeError:
                pass
            self.skip_split_key = keyboard.read_hotkey(False)
            try:
                if self.skip_split_key == self.splitLineEdit.text() or self.skip_split_key == self.resetLineEdit.text() or self.skip_split_key == self.skipsplitLineEdit.text() or self.skip_split_key == self.undosplitLineEdit.text():
                    self.skip_split_hotkey = keyboard.add_hotkey(self.old_skip_split_key, self.skipSplit)
                    self.afterSettingHotkeySignal.emit()
                    return
            except AttributeError:
                self.afterSettingHotkeySignal.emit()
                return
            try:
                if '+' in self.skip_split_key:
                    self.skip_split_hotkey = keyboard.add_hotkey(self.old_skip_split_key, self.skipSplit)
                    self.afterSettingHotkeySignal.emit()
                    return
            except AttributeError:
                self.afterSettingHotkeySignal.emit()
                return
            self.skip_split_hotkey = keyboard.add_hotkey(self.skip_split_key, self.skipSplit)
            self.skipsplitLineEdit.setText(self.skip_split_key)
            self.old_skip_split_key = self.skip_split_key
            self.afterSettingHotkeySignal.emit()
            return

        t = threading.Thread(target=callback)
        t.start()
        return

    def setUndoSplitHotkey(self):
        self.setundosplithotkeyButton.setText('Press a key..')
        self.beforeSettingHotkey()

        def callback():
            try:
                keyboard.remove_hotkey(self.undo_split_hotkey)
            except AttributeError:
                pass
            self.undo_split_key = keyboard.read_hotkey(False)
            try:
                if self.undo_split_key == self.splitLineEdit.text() or self.undo_split_key == self.resetLineEdit.text() or self.undo_split_key == self.skipsplitLineEdit.text() or self.undo_split_key == self.undosplitLineEdit.text():
                    self.undo_split_hotkey = keyboard.add_hotkey(self.old_undo_split_key, self.undoSplit)
                    self.afterSettingHotkeySignal.emit()
                    return
            except AttributeError:
                self.afterSettingHotkeySignal.emit()
                return
            try:
                if '+' in self.undo_split_key:
                    self.undo_split_hotkey = keyboard.add_hotkey(self.old_undo_split_key, self.undoSplit)
                    self.afterSettingHotkeySignal.emit()
                    return
            except AttributeError:
                self.afterSettingHotkeySignal.emit()
                return
            self.undo_split_hotkey = keyboard.add_hotkey(self.undo_split_key, self.undoSplit)
            self.undosplitLineEdit.setText(self.undo_split_key)
            self.old_undo_split_key = self.undo_split_key
            self.afterSettingHotkeySignal.emit()
            return

        t = threading.Thread(target=callback)
        t.start()
        return

    # do all of these after you click "set hotkey" but before you type the hotkey.
    def beforeSettingHotkey(self):
        self.startautosplitterButton.setEnabled(False)
        self.setsplithotkeyButton.setEnabled(False)
        self.setresethotkeyButton.setEnabled(False)
        self.setskipsplithotkeyButton.setEnabled(False)
        self.setundosplithotkeyButton.setEnabled(False)

    # do all of these things after you set a hotkey. a signal connects to this because
    # changing GUI stuff in the hotkey thread was causing problems
    def afterSettingHotkey(self):
        self.setsplithotkeyButton.setText('Set Hotkey')
        self.setresethotkeyButton.setText('Set Hotkey')
        self.setskipsplithotkeyButton.setText('Set Hotkey')
        self.setundosplithotkeyButton.setText('Set Hotkey')
        self.startautosplitterButton.setEnabled(True)
        self.setsplithotkeyButton.setEnabled(True)
        self.setresethotkeyButton.setEnabled(True)
        self.setskipsplithotkeyButton.setEnabled(True)
        self.setundosplithotkeyButton.setEnabled(True)
        return

    # check max FPS button connects here.
    def checkFPS(self):
        # error checking
        if self.splitimagefolderLineEdit.text() == 'No Folder Selected':
            self.splitImageDirectoryError()
            return
        for image in os.listdir(self.split_image_directory):
            if cv2.imread(self.split_image_directory + image, cv2.IMREAD_COLOR) is None:
                self.imageTypeError()
                return
            else:
                pass
        if self.hwnd == 0 or win32gui.GetWindowText(self.hwnd) == '':
            self.regionError()
            return
        if self.width == 0 or self.height == 0:
            self.regionSizeError()
            return

        # grab first image in the split image folder
        split_image_file = os.listdir(self.split_image_directory)[0]
        split_image_path = self.split_image_directory + split_image_file
        split_image = cv2.imread(split_image_path, cv2.IMREAD_COLOR)
        split_image = cv2.cvtColor(split_image, cv2.COLOR_BGR2RGB)
        split_image = cv2.resize(split_image, (self.RESIZE_WIDTH, self.RESIZE_HEIGHT))

        # run 10 iterations of screenshotting capture region + comparison.
        count = 0
        t0 = time.time()
        while count < 100:
            wDC = win32gui.GetWindowDC(self.hwnd)
            dcObj = win32ui.CreateDCFromHandle(wDC)
            cDC = dcObj.CreateCompatibleDC()
            bmp = win32ui.CreateBitmap()
            bmp.CreateCompatibleBitmap(dcObj, self.width, self.height)
            cDC.SelectObject(bmp)
            cDC.BitBlt((0, 0), (self.width, self.height), dcObj, (self.left, self.top), win32con.SRCCOPY)

            sct_img = bmp.GetBitmapBits(True)
            sct_img = np.frombuffer(sct_img, dtype='uint8')
            sct_img.shape = (self.height, self.width, 4)
            sct_img = cv2.resize(sct_img, (self.RESIZE_WIDTH, self.RESIZE_HEIGHT))
            sct_img = cv2.cvtColor(sct_img, cv2.COLOR_BGRA2RGB)

            # Cleanup
            dcObj.DeleteDC()
            cDC.DeleteDC()
            win32gui.ReleaseDC(self.hwnd, wDC)
            win32gui.DeleteObject(bmp.GetHandle())

            # comparison
            error = cv2.norm(split_image, sct_img, cv2.NORM_L2)
            max_error = 255 * 255
            for dimension in split_image.shape:
                max_error *= dimension
            max_error = max_error ** 0.5
            similarity = 1 - (error / max_error)

            count = count + 1

        # calculate FPS
        t1 = time.time()
        FPS = int(100 / (t1 - t0))
        FPS = str(FPS)
        self.fpsvalueLabel.setText(FPS)

    # undo split button and hotkey connect to here
    def undoSplit(self):
        # if the auto splitter is paused or the undo split button is enabled, do nothing.
        if self.undosplitButton.isEnabled() == False or self.split_image_number == 0:
            return

        # subtract 1 from the split image number
        self.split_image_number = self.split_image_number - 1

        # if i'ts the last split image, disable skip split button
        if self.split_image_number == self.number_of_split_images - 1:
            self.skipsplitButton.setEnabled(False)
        else:
            self.skipsplitButton.setEnabled(True)

        # if it's the first split image, disable the undo split button
        if self.split_image_number == 0:
            self.undosplitButton.setEnabled(False)
        else:
            self.undosplitButton.setEnabled(True)

        # draw updated current split image
        split_image_file = os.listdir(self.split_image_directory)[0 + self.split_image_number]
        split_image_path = self.split_image_directory + split_image_file
        split_image = cv2.imread(split_image_path, cv2.IMREAD_COLOR)
        split_image = cv2.cvtColor(split_image, cv2.COLOR_BGR2RGB)
        self.split_image = cv2.resize(split_image, (self.RESIZE_WIDTH, self.RESIZE_HEIGHT))
        self.split_image_display = cv2.resize(self.split_image, (240, 180))
        qImg = QtGui.QImage(self.split_image_display, self.split_image_display.shape[1],
                            self.split_image_display.shape[0], self.split_image_display.shape[1] * 3,
                            QtGui.QImage.Format_RGB888)
        self.updateCurrentSplitImage.emit(qImg)
        self.currentsplitimagefileLabel.setText(split_image_file)

        # set initial similarity and highest similarity to 0 and 0.001 respectively then return
        # to autosplitter comparison loop.
        self.similarity = 0
        self.highest_similarity = 0.001

        # small delay for double tap prevention
        time.sleep(0.1)

        return

    # skip split button and hotkey connect to here
    def skipSplit(self):

        if self.skipsplitButton.isEnabled() == False or self.split_image_number == self.number_of_split_images - 1:
            return

        self.split_image_number = self.split_image_number + 1

        if self.split_image_number == self.number_of_split_images - 1:
            self.skipsplitButton.setEnabled(False)
        else:
            self.skipsplitButton.setEnabled(True)
        if self.split_image_number == 0:
            self.undosplitButton.setEnabled(False)
        else:
            self.undosplitButton.setEnabled(True)

            # draw updated current split image
        split_image_file = os.listdir(self.split_image_directory)[0 + self.split_image_number]
        split_image_path = self.split_image_directory + split_image_file
        split_image = cv2.imread(split_image_path, cv2.IMREAD_COLOR)
        split_image = cv2.cvtColor(split_image, cv2.COLOR_BGR2RGB)
        self.split_image = cv2.resize(split_image, (self.RESIZE_WIDTH, self.RESIZE_HEIGHT))
        self.split_image_display = cv2.resize(self.split_image, (240, 180))
        qImg = QtGui.QImage(self.split_image_display, self.split_image_display.shape[1],
                            self.split_image_display.shape[0], self.split_image_display.shape[1] * 3,
                            QtGui.QImage.Format_RGB888)
        self.updateCurrentSplitImage.emit(qImg)
        self.currentsplitimagefileLabel.setText(split_image_file)

        self.similarity = 0
        self.highest_similarity = 0.001
        
        time.sleep(0.1)
        return

    # reset button and hotkey connects here.
    def reset(self):
        self.startautosplitterButton.setText('Start Auto Splitter')
        return

    # split hotkey connects to this function, which then returns to the GUI thread
    # by emitting the signal and starts the autosplitter function
    def startAutoSplitter(self):
        # if the auto splitter is already running or the button is disabled, don't emit the signal to start it.
        if self.startautosplitterButton.text() == 'Running..' or self.startautosplitterButton.isEnabled() == False:
            return
        else:
            self.startAutoSplitterSignal.emit()

    def autoSplitter(self):
        # error checking:
        if self.splitimagefolderLineEdit.text() == 'No Folder Selected':
            self.splitImageDirectoryError()
            return
        if self.hwnd == 0 or win32gui.GetWindowText(self.hwnd) == '':
            self.regionError()
            return
        # checks to make sure every file in the split image folder can be opened by opencv
        for image in os.listdir(self.split_image_directory):
            if cv2.imread(self.split_image_directory + image, cv2.IMREAD_COLOR) is None:
                self.imageTypeError()
                return
            else:
                pass
        if self.splitLineEdit.text() == '':
            self.splitHotkeyError()
            return

        # change auto splitter button text and disable/enable some buttons
        self.startautosplitterButton.setText('Running..')
        self.browseButton.setEnabled(False)
        self.startautosplitterButton.setEnabled(False)
        self.resetButton.setEnabled(True)
        self.undosplitButton.setEnabled(True)
        self.skipsplitButton.setEnabled(True)
        self.setsplithotkeyButton.setEnabled(False)
        self.setresethotkeyButton.setEnabled(False)
        self.setskipsplithotkeyButton.setEnabled(False)
        self.setundosplithotkeyButton.setEnabled(False)

        self.split_image_number = 0
        self.number_of_split_images = len(os.listdir(self.split_image_directory))

        # First while loop: stays in this loop until all of the split images have been split
        while self.split_image_number < self.number_of_split_images:
            # open split image, resize, set to current split image
            split_image_file = os.listdir(self.split_image_directory)[0 + self.split_image_number]
            split_image_path = self.split_image_directory + split_image_file
            split_image = cv2.imread(split_image_path, cv2.IMREAD_COLOR)
            split_image = cv2.cvtColor(split_image, cv2.COLOR_BGR2RGB)
            self.split_image = cv2.resize(split_image, (self.RESIZE_WIDTH, self.RESIZE_HEIGHT))
            self.split_image_display = cv2.resize(self.split_image, (240, 180))
            qImg = QtGui.QImage(self.split_image_display, self.split_image_display.shape[1],
                                self.split_image_display.shape[0], self.split_image_display.shape[1] * 3,
                                QtGui.QImage.Format_RGB888)
            self.updateCurrentSplitImage.emit(qImg)
            self.currentsplitimagefileLabel.setText(split_image_file)

            self.similarity = 0
            self.highest_similarity = 0.001

            # second while loop: stays in this loop until similarity threshold is met
            start = time.time()
            while self.similarity < self.similaritythresholdDoubleSpinBox.value():
                # reset if the set screen region window was closed
                if win32gui.GetWindowText(self.hwnd) == '':
                    self.reset()
                # loop goes into here if start auto splitter text is "Start Auto Splitter"
                if self.startautosplitterButton.text() == 'Start Auto Splitter':
                    self.currentSplitImage.setText(' ')
                    self.currentsplitimagefileLabel.setText(' ')
                    self.livesimilarityLabel.setText(' ')
                    self.highestsimilarityLabel.setText(' ')
                    self.browseButton.setEnabled(True)
                    self.startautosplitterButton.setEnabled(True)
                    self.resetButton.setEnabled(False)
                    self.undosplitButton.setEnabled(False)
                    self.skipsplitButton.setEnabled(False)
                    self.setsplithotkeyButton.setEnabled(True)
                    self.setresethotkeyButton.setEnabled(True)
                    self.setskipsplithotkeyButton.setEnabled(True)
                    self.setundosplithotkeyButton.setEnabled(True)
                    return

                # grab screenshot of capture region
                wDC = win32gui.GetWindowDC(self.hwnd)
                dcObj = win32ui.CreateDCFromHandle(wDC)
                cDC = dcObj.CreateCompatibleDC()
                bmp = win32ui.CreateBitmap()
                bmp.CreateCompatibleBitmap(dcObj, self.width, self.height)
                cDC.SelectObject(bmp)
                cDC.BitBlt((0, 0), (self.width, self.height), dcObj, (self.left, self.top), win32con.SRCCOPY)

                self.sct_img = bmp.GetBitmapBits(True)
                self.sct_img = np.frombuffer(self.sct_img, dtype='uint8')
                self.sct_img.shape = (self.height, self.width, 4)
                self.sct_img = cv2.resize(self.sct_img, (self.RESIZE_WIDTH, self.RESIZE_HEIGHT))
                self.sct_img = cv2.cvtColor(self.sct_img, cv2.COLOR_BGRA2RGB)

                # Cleanup
                dcObj.DeleteDC()
                cDC.DeleteDC()
                win32gui.ReleaseDC(self.hwnd, wDC)
                win32gui.DeleteObject(bmp.GetHandle())

                # calculate similarity
                error = cv2.norm(self.split_image, self.sct_img, cv2.NORM_L2)
                max_error = (self.split_image.size ** 0.5) * 255
                self.similarity = 1 - (error / max_error)

                # show live similarity if the checkbox is checked
                if self.showlivesimilarityCheckBox.isChecked():
                    self.livesimilarityLabel.setText(str(self.similarity)[:4])
                else:
                    self.livesimilarityLabel.setText(' ')

                # if the similarity becomes higher than highest similarity, set it as such.
                if self.similarity > self.highest_similarity:
                    self.highest_similarity = self.similarity

                # show live highest similarity if the checkbox is checked
                if self.showhighestsimilarityCheckBox.isChecked():
                    self.highestsimilarityLabel.setText(str(self.highest_similarity)[:4])
                else:
                    self.highestsimilarityLabel.setText(' ')

                # if its the last split image, disable the skip split button
                if self.split_image_number == self.number_of_split_images - 1:
                    self.skipsplitButton.setEnabled(False)
                else:
                    self.skipsplitButton.setEnabled(True)

                # if its the first split image, disable the undo split button
                if self.split_image_number == 0:
                    self.undosplitButton.setEnabled(False)
                else:
                    self.undosplitButton.setEnabled(True)

                # limit the number of time the comparison runs to reduce cpu usage
                fps_limit = self.fpslimitSpinBox.value()
                time.sleep((1 / fps_limit) - (time.time() - start) % (1 / fps_limit))
                QtGui.QApplication.processEvents()

            # comes here when threshold gets met

            # send the split key
            keyboard.send(str(self.splitLineEdit.text()))

            # add one to the split image number
            self.split_image_number = self.split_image_number + 1

            # set a "pause" split image number. This is done so that it can detect if user hit split/undo split while paused.
            pause_split_image_number = self.split_image_number

            # if its not the last split image, pause for the amount set by the user
            if self.number_of_split_images != self.split_image_number:
                #set current split image to none
                self.currentSplitImage.setText('none (paused)')
                self.currentsplitimagefileLabel.setText(' ')
                self.currentSplitImage.setAlignment(QtCore.Qt.AlignCenter)

                # if its the first split image, disable the undo split button
                if self.split_image_number == 0:
                    self.undosplitButton.setEnabled(False)
                else:
                    self.undosplitButton.setEnabled(True)

                # if its the last split image, disable the skip split button
                if self.split_image_number == self.number_of_split_images - 1:
                    self.skipsplitButton.setEnabled(False)
                else:
                    self.skipsplitButton.setEnabled(True)

                QtGui.QApplication.processEvents()

                # I have a pause loop here so that it can check if the user presses skip split, undo split, or reset here.
                # This should probably eventually be a signal... but it works
                start = time.time()
                while time.time() - start < self.pauseSpinBox.value():
                    # check for reset
                    if win32gui.GetWindowText(self.hwnd) == '':
                        self.reset()
                    if self.startautosplitterButton.text() == 'Start Auto Splitter':
                        self.currentSplitImage.setText(' ')
                        self.currentsplitimagefileLabel.setText(' ')
                        self.livesimilarityLabel.setText(' ')
                        self.highestsimilarityLabel.setText(' ')
                        self.browseButton.setEnabled(True)
                        self.startautosplitterButton.setEnabled(True)
                        self.resetButton.setEnabled(False)
                        self.undosplitButton.setEnabled(False)
                        self.skipsplitButton.setEnabled(False)
                        self.setsplithotkeyButton.setEnabled(True)
                        self.setresethotkeyButton.setEnabled(True)
                        self.setskipsplithotkeyButton.setEnabled(True)
                        self.setundosplithotkeyButton.setEnabled(True)
                        return
                    # check for skip/undo split:
                    if self.split_image_number != pause_split_image_number:
                        break

                    QtTest.QTest.qWait(1)

        # loop breaks to here when the last image splits
        self.startautosplitterButton.setText('Start Auto Splitter')
        self.currentSplitImage.setText(' ')
        self.currentsplitimagefileLabel.setText(' ')
        self.livesimilarityLabel.setText(' ')
        self.highestsimilarityLabel.setText(' ')
        self.browseButton.setEnabled(True)
        self.startautosplitterButton.setEnabled(True)
        self.resetButton.setEnabled(False)
        self.undosplitButton.setEnabled(False)
        self.skipsplitButton.setEnabled(False)
        self.setsplithotkeyButton.setEnabled(True)
        self.setresethotkeyButton.setEnabled(True)
        self.setskipsplithotkeyButton.setEnabled(True)
        self.setundosplithotkeyButton.setEnabled(True)
        QtGui.QApplication.processEvents()

        # Error messages

    def splitImageDirectoryError(self):
        msgBox = QtGui.QMessageBox()
        msgBox.setWindowTitle('Error')
        msgBox.setText("No split image folder is selected.")
        msgBox.exec_()

    def imageTypeError(self):
        msgBox = QtGui.QMessageBox()
        msgBox.setWindowTitle('Error')
        msgBox.setText("All files in split image folder must be valid image files.")
        msgBox.exec_()

    def regionError(self):
        msgBox = QtGui.QMessageBox()
        msgBox.setWindowTitle('Error')
        msgBox.setText("No region is selected.")
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

    # exit safely when closing the window
    def closeEvent(self, app):
        # save settings to .pkl file.
        self.split_image_directory = str(self.splitimagefolderLineEdit.text())
        self.similarity_threshold = self.similaritythresholdDoubleSpinBox.value()
        self.pause = self.pauseSpinBox.value()
        self.fps_limit = self.fpslimitSpinBox.value()
        self.split_key = str(self.splitLineEdit.text())
        self.reset_key = str(self.resetLineEdit.text())
        self.skip_split_key = str(self.skipsplitLineEdit.text())
        self.undo_split_key = str(self.undosplitLineEdit.text())

        with open('settings.pkl', 'wb') as f:
            pickle.dump(
                [self.split_image_directory, self.similarity_threshold, self.pause, self.fps_limit, self.split_key,
                 self.reset_key, self.skip_split_key, self.undo_split_key], f)
        sys.exit()


# Widget for dragging screen region
# https://github.com/harupy/snipping-tool
class SelectRegionWidget(QtGui.QWidget):
    def __init__(self):
        super(SelectRegionWidget, self).__init__()
        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()
        screen_width = user32.GetSystemMetrics(78)
        screen_height = user32.GetSystemMetrics(79)
        self.setGeometry(0, 0, screen_width, screen_height)
        self.setWindowTitle(' ')

        self.height = -1
        self.width = -1

        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()
        self.setWindowOpacity(0.5)
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.show()

    def paintEvent(self, event):
        qp = QtGui.QPainter(self)
        qp.setPen(QtGui.QPen(QtGui.QColor('red'), 2))
        qp.setBrush(QtGui.QColor('opaque'))
        qp.drawRect(QtCore.QRect(self.begin, self.end))

    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = self.begin
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.close()

        self.x1 = min(self.begin.x(), self.end.x())
        self.y1 = min(self.begin.y(), self.end.y())
        self.x2 = max(self.begin.x(), self.end.x())
        self.y2 = max(self.begin.y(), self.end.y())

        self.height = self.y2 - self.y1
        self.width = self.x2 - self.x1


# About Window
class AboutWidget(QtGui.QWidget, about.Ui_aboutAutoSplitWidget):
    def __init__(self):
        super(AboutWidget, self).__init__()
        self.setupUi(self)
        self.createdbyLabel.setOpenExternalLinks(True)
        self.donatebuttonLabel.setOpenExternalLinks(True)
        self.show()


def main():
    global app
    app = QtGui.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('icon.ico'))
    w = AutoSplit()
    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
