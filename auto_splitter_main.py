from PyQt4 import QtGui, QtCore
from PyQt4.QtTest import QTest
from PyQt4 import QtTest
from PIL import Image
from image_match.goldberg import ImageSignature
import sys
import os
import win32con
import win32gui
import win32ui
import cv2
import time
import tkinter as tk
import ctypes.wintypes
import ctypes
import numpy as np
import keyboard
import threading
import auto_splitter_design

class AutoSplit(QtGui.QMainWindow, auto_splitter_design.Ui_MainWindow):
    updateCurrentSplitImage = QtCore.pyqtSignal(QtGui.QImage)
    startAutoSplitterSignal = QtCore.pyqtSignal()
    afterPressingHotkeySignal = QtCore.pyqtSignal()
        
    def __init__(self, parent=None):      
        super(AutoSplit, self).__init__(parent)
        self.setupUi(self)
        
        app.aboutToQuit.connect(self.closeEvent)
        
        self.undosplitButton.setEnabled(False)
        self.skipsplitButton.setEnabled(False)
        self.resetButton.setEnabled(False)

        #set hwnd (the capture region window) to 0 initially 
        self.hwnd = 0
        
        #when using select screen region, left is off by a few pixels? user can easily adjust this..
        self.offset = 0
        
        #RESIZE DIMENSIONS
        self.RESIZE_WIDTH = 160
        self.RESIZE_HEIGHT = 120
        
        #split image folder line edit text, might put into initial layout
        self.splitimagefolderLineEdit.setText('No Folder Selected')
        
        #Click browse button
        self.browseButton.clicked.connect(self.browse)
        
        #Click select region button
        self.selectregionButton.clicked.connect(self.selectRegion)
        
        #Click Position buttons
        self.positionUpButton.clicked.connect(self.positionUp)
        self.positionRightButton.clicked.connect(self.positionRight)
        self.positionDownButton.clicked.connect(self.positionDown)
        self.positionLeftButton.clicked.connect(self.positionLeft)
        
        #Click width or height SpinBox
        self.widthSpinBox.valueChanged.connect(self.updateWidth)
        self.heightSpinBox.valueChanged.connect(self.updateHeight)
        
        
        self.liveimageCheckBox.clicked.connect(self.checkLiveImage)
        self.timerLiveImage = QtCore.QTimer()
        self.timerLiveImage.timeout.connect(self.live_image)
        
        self.startautosplitterButton.clicked.connect(self.autoSplitter)
        
        self.checkfpsButton.clicked.connect(self.checkFPS)
        
        self.resetButton.clicked.connect(self.reset)
        
        self.skipsplitButton.clicked.connect(self.skipSplit)
        
        self.undosplitButton.clicked.connect(self.undoSplit)
        
        self.setsplithotkeyButton.clicked.connect(self.setSplitHotkey)
        self.setresethotkeyButton.clicked.connect(self.setResetHotkey)
        self.setskipsplithotkeyButton.clicked.connect(self.setSkipSplitHotkey)
        self.setundosplithotkeyButton.clicked.connect(self.setUndoSplitHotkey)
        
        #signals
        self.updateCurrentSplitImage.connect(self.updated_split)
        self.startAutoSplitterSignal.connect(self.autoSplitter)
        self.afterPressingHotkeySignal.connect(self.afterPressingHotkey)
    
    def afterPressingHotkey(self):
        self.setsplithotkeyButton.setText('Set Hotkey')
        self.setresethotkeyButton.setText('Set Hotkey')
        self.setskipsplithotkeyButton.setText('Set Hotkey')
        self.setundosplithotkeyButton.setText('Set Hotkey')
        self.setsplithotkeyButton.setEnabled(True)
        self.setresethotkeyButton.setEnabled(True)
        self.setskipsplithotkeyButton.setEnabled(True)
        self.setundosplithotkeyButton.setEnabled(True)
        
    def startAutoSplitter(self):
        #if the auto splitter is already running, don't emit the signal to start it again.
        if self.startautosplitterButton.text() == 'Running..':
            return
        self.startAutoSplitterSignal.emit()
        
    def updated_split(self, qImg):
        pix = QtGui.QPixmap(qImg)
        self.currentSplitImage.setPixmap(pix)
    
    def closeEvent(self, app):
        sys.exit()
        
    def split_image_directory_error(self):
        msgBox = QtGui.QMessageBox()
        msgBox.setWindowTitle('error')
        msgBox.setText("no split image folder is selected")
        msgBox.exec_()
    
    def image_type_error(self):
        msgBox = QtGui.QMessageBox()
        msgBox.setWindowTitle('error')
        msgBox.setText("all images in folder must be .png")
        msgBox.exec_()
    
    def region_error(self):
        msgBox = QtGui.QMessageBox()
        msgBox.setWindowTitle('error')
        msgBox.setText("no region is selected")
        msgBox.exec_()
    def regionSizeError(self):
        msgBox = QtGui.QMessageBox()
        msgBox.setWindowTitle('error')
        msgBox.setText("width and height cannot be 0")
        msgBox.exec_()
    
    def split_hotkey_error(self):
        msgBox = QtGui.QMessageBox()
        msgBox.setWindowTitle('error')
        msgBox.setText("no split hotkey has been set")
        msgBox.exec_()
    
    def setSplitHotkey(self):
        self.setsplithotkeyButton.setText('Press a key..')
        self.setsplithotkeyButton.setEnabled(False)
        self.setresethotkeyButton.setEnabled(False)
        self.setskipsplithotkeyButton.setEnabled(False)
        self.setundosplithotkeyButton.setEnabled(False)
        def callback():
            try:
                keyboard.remove_hotkey(self.split_hotkey)
            except AttributeError:
                pass
            self.split_key = keyboard.read_hotkey()
            #if split key equal to anything in the lineedits, do nothing
            if self.split_key == self.splitLineEdit.text() or self.split_key == self.resetLineEdit.text() or self.split_key == self.skipsplitLineEdit.text() or self.split_key == self.undosplitLineEdit.text():
                self.split_hotkey = keyboard.add_hotkey(self.old_split_key, self.startAutoSplitter)
                self.afterPressingHotkeySignal.emit()
                return
            #if hit multiple keys, do nothing
            if '+' in self.split_key:
                self.split_hotkey = keyboard.add_hotkey(self.old_split_key, self.startAutoSplitter)
                self.afterPressingHotkeySignal.emit()
                return
            self.split_hotkey = keyboard.add_hotkey(self.split_key, self.startAutoSplitter)
            self.splitLineEdit.setText(self.split_key)
            self.old_split_key = self.split_key
            self.afterPressingHotkeySignal.emit()
            return
        t = threading.Thread(target=callback)
        t.start()
        return
        
    def setResetHotkey(self):
        self.setresethotkeyButton.setText('Press a key..')
        self.setsplithotkeyButton.setEnabled(False)
        self.setresethotkeyButton.setEnabled(False)
        self.setskipsplithotkeyButton.setEnabled(False)
        self.setundosplithotkeyButton.setEnabled(False)
        def callback():
            try:
                keyboard.remove_hotkey(self.reset_hotkey)
            except AttributeError:
                pass
            self.reset_key = keyboard.read_hotkey()
            if self.reset_key == self.splitLineEdit.text() or self.reset_key== self.resetLineEdit.text() or self.reset_key == self.skipsplitLineEdit.text() or self.reset_key == self.undosplitLineEdit.text():
                self.reset_hotkey = keyboard.add_hotkey(self.old_reset_key, self.reset)
                self.afterPressingHotkeySignal.emit()
                return
            #if hit multiple keys, do nothing
            if '+' in self.reset_key:
                self.reset_hotkey = keyboard.add_hotkey(self.old_reset_key, self.reset)
                self.afterPressingHotkeySignal.emit()
                return
            self.reset_hotkey = keyboard.add_hotkey(self.reset_key, self.reset)
            self.resetLineEdit.setText(self.reset_key)
            self.old_reset_key = self.reset_key
            self.afterPressingHotkeySignal.emit()
            return
        t = threading.Thread(target=callback)
        t.start()
        return
        
    def setSkipSplitHotkey(self):
        self.setskipsplithotkeyButton.setText('Press a key..')
        self.setsplithotkeyButton.setEnabled(False)
        self.setresethotkeyButton.setEnabled(False)
        self.setskipsplithotkeyButton.setEnabled(False)
        self.setundosplithotkeyButton.setEnabled(False)
        def callback():
            try:
                keyboard.remove_hotkey(self.skip_split_hotkey)
            except AttributeError:
                pass
            self.skip_split_key = keyboard.read_hotkey()
            if self.skip_split_key == self.splitLineEdit.text() or self.skip_split_key == self.resetLineEdit.text() or self.skip_split_key == self.skipsplitLineEdit.text() or self.skip_split_key == self.undosplitLineEdit.text():
                self.skip_split_hotkey = keyboard.add_hotkey(self.old_skip_split_key, self.skipSplit)
                self.afterPressingHotkeySignal.emit()
                return
            #if hit multiple keys, do nothing
            if '+' in self.skip_split_key:
                self.skip_split_hotkey = keyboard.add_hotkey(self.old_skip_split_key, self.skipSplit)
                self.afterPressingHotkeySignal.emit()
                return
            self.skip_split_hotkey = keyboard.add_hotkey(self.skip_split_key, self.skipSplit)
            self.skipsplitLineEdit.setText(self.skip_split_key)
            self.old_skip_split_key = self.skip_split_key
            self.afterPressingHotkeySignal.emit()
            return
        t = threading.Thread(target=callback)
        t.start()
        return
    
    def setUndoSplitHotkey(self):
        self.setundosplithotkeyButton.setText('Press a key..')
        self.setsplithotkeyButton.setEnabled(False)
        self.setresethotkeyButton.setEnabled(False)
        self.setskipsplithotkeyButton.setEnabled(False)
        self.setundosplithotkeyButton.setEnabled(False)
        def callback():
            try:
                keyboard.remove_hotkey(self.undo_split_hotkey)
            except AttributeError:
                pass
            self.undo_split_key = keyboard.read_hotkey()
            if self.undo_split_key == self.splitLineEdit.text() or self.undo_split_key == self.resetLineEdit.text() or self.undo_split_key == self.skipsplitLineEdit.text() or self.undo_split_key == self.undosplitLineEdit.text():
                self.undo_split_hotkey = keyboard.add_hotkey(self.old_undo_split_key, self.undoSplit)
                self.afterPressingHotkeySignal.emit()
                return
            #if hit multiple keys, do nothing
            if '+' in self.undo_split_key:
                self.undo_split_hotkey = keyboard.add_hotkey(self.old_undo_split_key, self.undoSplit)
                self.afterPressingHotkeySignal.emit()
                return
            self.undo_split_hotkey = keyboard.add_hotkey(self.undo_split_key, self.undoSplit)
            self.undosplitLineEdit.setText(self.undo_split_key)
            self.old_undo_split_key = self.undo_split_key
            self.afterPressingHotkeySignal.emit()
            return
        t = threading.Thread(target=callback)
        t.start()
        return
        
        
    def checkLiveImage(self):
        if self.liveimageCheckBox.isChecked():
            self.timerLiveImage.start(1000/60)
        else:
            self.timerLiveImage.stop()
            self.live_image()
    
    def positionUp(self):
        try:
            self.y1 = self.y1 - 1
        except AttributeError:
            pass
              
    def positionRight(self):
        try:
            self.x1 = self.x1 + 1
        except AttributeError:
            pass
    
    def positionDown(self):
        try:
            self.y1 = self.y1 + 1
        except AttributeError:
            pass
    
    def positionLeft(self):
        try:
            self.x1 = self.x1 - 1
        except AttributeError:
            pass
        
    def updateWidth(self):
        self.width = self.widthSpinBox.value()
        
    def updateHeight(self):
        self.height = self.heightSpinBox.value()
        
    def browse(self):
        self.split_image_directory = str(QtGui.QFileDialog.getExistingDirectory(self, "Select Split Image Directory"))+'\\'
        if self.split_image_directory == '\\':
            self.split_image_directory = 'No Folder Selected'
        self.splitimagefolderLineEdit.setText(self.split_image_directory)
    
    def selectRegion(self):
        #call screen region widget
        self.SelectRegionWidget = SelectRegionWidget()
        
        #wait until height and width change until we set them to the spinboxes
        while self.SelectRegionWidget.height == -1 and self.SelectRegionWidget.width == -1:
            QTest.qWait(1)
        
        #return if width or height are zero.
        if self.SelectRegionWidget.width == 0 or self.SelectRegionWidget.height == 0:
            self.regionSizeError()
            return
        
        #change width and height lineedits. 
        self.widthSpinBox.setValue(self.SelectRegionWidget.width)
        self.heightSpinBox.setValue(self.SelectRegionWidget.height)
        
        #update AutoSplitter x1,y1,width,height values
        self.x1 = self.SelectRegionWidget.x1
        self.y1 = self.SelectRegionWidget.y1
        self.width = self.SelectRegionWidget.width
        self.height = self.SelectRegionWidget.height
        
        #update selected window
        self.hwnd = win32gui.WindowFromPoint((self.x1, self.y1))
        while win32gui.IsChild(win32gui.GetParent(self.hwnd), self.hwnd):
            self.hwnd = win32gui.GetParent(self.hwnd)
        DwmGetWindowAttribute = ctypes.windll.dwmapi.DwmGetWindowAttribute
        DWMWA_EXTENDED_FRAME_BOUNDS = 9
        rect = ctypes.wintypes.RECT()
        DwmGetWindowAttribute(self.hwnd,
                      ctypes.wintypes.DWORD(DWMWA_EXTENDED_FRAME_BOUNDS),
                      ctypes.byref(rect),
                      ctypes.sizeof(rect)
                      )
        
        self.top_old = rect.top
        self.left_old = rect.left
        
        #check live image
        self.checkLiveImage()
    
    def live_image(self):
        try:
            DwmGetWindowAttribute = ctypes.windll.dwmapi.DwmGetWindowAttribute
            DWMWA_EXTENDED_FRAME_BOUNDS = 9
            rect = ctypes.wintypes.RECT()
            DwmGetWindowAttribute(self.hwnd,
                        ctypes.wintypes.DWORD(DWMWA_EXTENDED_FRAME_BOUNDS),
                        ctypes.byref(rect),
                        ctypes.sizeof(rect)
                        )
    
            self.top = self.y1 - self.top_old
            self.left = self.x1 - self.left_old + self.offset
    
            
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
    
            img = cv2.resize(img, (240, 180)) #Resize to match the label size
    
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
    
            #Convert to set it on the label
            qImg = QtGui.QImage(img, img.shape[1], img.shape[0], img.shape[1]*3, QtGui.QImage.Format_RGB888)
            pix = QtGui.QPixmap(qImg)
            self.liveImage.setPixmap(pix)
            
            #Cleanup
            dcObj.DeleteDC()
            cDC.DeleteDC()
            win32gui.ReleaseDC(self.hwnd, wDC)
            win32gui.DeleteObject(bmp.GetHandle())
        except AttributeError:
            pass
            
    
    def reset(self):
        if self.currentSplitImage.text() == 'none (paused)':
            return
        self.startautosplitterButton.setText('Start Auto Splitter')
        return
    
        
    def undoSplit(self):

        if self.currentSplitImage.text()=='none (paused)' or self.undosplitButton.isEnabled() == False or self.split_image_number == 0:
            return
            
        time.sleep(0.2)   
        self.split_image_number = self.split_image_number-1
        if self.split_image_number == self.number_of_split_images-1:
            self.skipsplitButton.setEnabled(False)
        else:
            self.skipsplitButton.setEnabled(True)
        if self.split_image_number == 0:
            self.undosplitButton.setEnabled(False)
        else:
            self.undosplitButton.setEnabled(True)
        #draw updated current split image
        split_image_file=os.listdir(self.split_image_directory)[0+self.split_image_number]
        split_image_path=self.split_image_directory+split_image_file
        split_image = cv2.imread(split_image_path, cv2.IMREAD_COLOR)
        split_image = cv2.resize(split_image, (240, 180))
        split_image = cv2.cvtColor(split_image, cv2.COLOR_BGR2RGB)
        qImg = QtGui.QImage(split_image, split_image.shape[1], split_image.shape[0], split_image.shape[1]*3, QtGui.QImage.Format_RGB888)    
        self.updateCurrentSplitImage.emit(qImg)
        
        split_image = Image.open(split_image_path)
        split_image = split_image.convert('RGB')
        split_image_resized=split_image.resize((self.RESIZE_WIDTH,self.RESIZE_HEIGHT))
        split_image = np.array(split_image_resized)
        gis = ImageSignature()
        self.split_image_signature = gis.generate_signature(split_image)
            
        self.similarity = 0
        self.highest_similarity=0.001
        return
    
    def skipSplit(self):
        
        if self.currentSplitImage.text()=='none (paused)' or self.skipsplitButton.isEnabled() == False or self.split_image_number == self.number_of_split_images-1:
            return
        
        time.sleep(0.2)
        self.split_image_number = self.split_image_number+1
        if self.split_image_number == self.number_of_split_images-1:
            self.skipsplitButton.setEnabled(False)
        else:
            self.skipsplitButton.setEnabled(True)
        if self.split_image_number == 0:
            self.undosplitButton.setEnabled(False)
        else:
            self.undosplitButton.setEnabled(True)             
        
        #draw updated current split image
        split_image_file=os.listdir(self.split_image_directory)[0+self.split_image_number]
        split_image_path=self.split_image_directory+split_image_file
        split_image = cv2.imread(split_image_path, cv2.IMREAD_COLOR)
        split_image = cv2.resize(split_image, (240, 180))
        split_image = cv2.cvtColor(split_image, cv2.COLOR_BGR2RGB)
        qImg = QtGui.QImage(split_image, split_image.shape[1], split_image.shape[0], split_image.shape[1]*3, QtGui.QImage.Format_RGB888)    
        self.updateCurrentSplitImage.emit(qImg)
 
        split_image = Image.open(split_image_path)
        split_image = split_image.convert('RGB')
        split_image_resized=split_image.resize((self.RESIZE_WIDTH,self.RESIZE_HEIGHT))
        split_image = np.array(split_image_resized)
        gis = ImageSignature()
        self.split_image_signature = gis.generate_signature(split_image)
        
        self.similarity = 0
        self.highest_similarity=0.001
        return

    
    def checkFPS(self):
        #error checking
        if self.splitimagefolderLineEdit.text() == 'No Folder Selected':
            self.split_image_directory_error()
            return
        
        if not all(File.endswith(".png") or File.endswith(".PNG") for File in os.listdir(self.split_image_directory)):
            self.image_type_error()
            return
        
        if self.hwnd == 0:
            self.region_error()
            return
        
        if self.width == 0 or self.height == 0:
            self.regionSizeError()
            return
            
        split_image_file=os.listdir(self.split_image_directory)[0]
        split_image_path=self.split_image_directory+split_image_file
        split_image = Image.open(split_image_path)
        split_image = split_image.convert('RGB')
        split_image_resized=split_image.resize((self.RESIZE_WIDTH,self.RESIZE_HEIGHT))
        split_image = np.array(split_image_resized)
        gis = ImageSignature()
        split_image_signature = gis.generate_signature(split_image)
        
        count=0
        t0=time.time()
        while count < 10:
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
            sct_img = cv2.resize(sct_img, (self.RESIZE_WIDTH,self.RESIZE_HEIGHT))
 
            #Cleanup
            dcObj.DeleteDC()
            cDC.DeleteDC()
            win32gui.ReleaseDC(self.hwnd, wDC)
            win32gui.DeleteObject(bmp.GetHandle())
                
            sct_img_signature = gis.generate_signature(sct_img)
            normalized_distance = gis.normalized_distance(split_image_signature, sct_img_signature)
            count=count+1
        
        t1 = time.time()
        FPS=int(10/(t1-t0))
        FPS=str(FPS)
        self.fpsvalueLabel.setText(FPS)
            
    def autoSplitter(self):
        #error checking:
        
        if self.splitimagefolderLineEdit.text() == 'No Folder Selected':
            self.split_image_directory_error()
            return
        
        if not all(File.endswith(".png") or File.endswith(".PNG") for File in os.listdir(self.split_image_directory)):
            self.image_type_error()
            return
        
        if self.hwnd == 0:
            self.region_error()
            return      
        
        if self.splitLineEdit.text() == '':
            self.split_hotkey_error()
            return
        self.startautosplitterButton.setText('Running..')
        self.startautosplitterButton.setEnabled(False)
        self.resetButton.setEnabled(True)
        self.undosplitButton.setEnabled(True)
        self.skipsplitButton.setEnabled(True)
        self.setsplithotkeyButton.setEnabled(False)
        self.setresethotkeyButton.setEnabled(False)
        self.setskipsplithotkeyButton.setEnabled(False)
        self.setundosplithotkeyButton.setEnabled(False)
        
        self.split_image_number=0
        self.number_of_split_images=len(os.listdir(self.split_image_directory))
        while self.split_image_number < self.number_of_split_images:
            #open split image, resize, get signature and set it to the current split image label
            split_image_file=os.listdir(self.split_image_directory)[0+self.split_image_number]
            split_image_path=self.split_image_directory+split_image_file
            split_image = cv2.imread(split_image_path, cv2.IMREAD_COLOR)
            split_image = cv2.resize(split_image, (240, 180))
            split_image = cv2.cvtColor(split_image, cv2.COLOR_BGR2RGB)
            qImg = QtGui.QImage(split_image, split_image.shape[1], split_image.shape[0], split_image.shape[1]*3, QtGui.QImage.Format_RGB888)    
            self.updateCurrentSplitImage.emit(qImg)
        
            split_image = Image.open(split_image_path)
            split_image = split_image.convert('RGB')
            split_image_resized=split_image.resize((self.RESIZE_WIDTH,self.RESIZE_HEIGHT))
            split_image = np.array(split_image_resized)
            gis = ImageSignature()
            self.split_image_signature = gis.generate_signature(split_image)
            
            self.similarity = 0
            self.highest_similarity=0.001
            while self.similarity < self.similaritythresholdDoubleSpinBox.value():
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
                self.sct_img = cv2.resize(self.sct_img, (self.RESIZE_WIDTH,self.RESIZE_HEIGHT))
 
                #Cleanup
                dcObj.DeleteDC()
                cDC.DeleteDC()
                win32gui.ReleaseDC(self.hwnd, wDC)
                win32gui.DeleteObject(bmp.GetHandle())
                
                sct_img_signature = gis.generate_signature(self.sct_img)
                normalized_distance = gis.normalized_distance(self.split_image_signature, sct_img_signature)
                self.similarity = 1 - normalized_distance
                
                #live similarity
                if self.showlivesimilarityCheckBox.isChecked():
                    self.livesimilarityLabel.setText(str(self.similarity)[:4])
                else:
                    self.livesimilarityLabel.setText(' ')
                
                #live highest similarity
                if self.similarity > self.highest_similarity:
                    self.highest_similarity = self.similarity
                if self.showhighestsimilarityCheckBox.isChecked():
                    self.highestsimilarityLabel.setText(str(self.highest_similarity)[:4])
                else:
                    self.highestsimilarityLabel.setText(' ')
                if self.split_image_number == self.number_of_split_images-1:
                    self.skipsplitButton.setEnabled(False)
                else:
                    self.skipsplitButton.setEnabled(True)
                if self.split_image_number == 0:
                    self.undosplitButton.setEnabled(False)
                else:
                    self.undosplitButton.setEnabled(True)             
                
                #when reset button is pushed:
                if self.startautosplitterButton.text() == 'Start Auto Splitter':
                    self.currentSplitImage.setText(' ')
                    self.livesimilarityLabel.setText(' ')
                    self.highestsimilarityLabel.setText(' ')
                    self.startautosplitterButton.setEnabled(True)
                    self.resetButton.setEnabled(False)
                    self.undosplitButton.setEnabled(False)
                    self.skipsplitButton.setEnabled(False)
                    self.setsplithotkeyButton.setEnabled(True)
                    self.setresethotkeyButton.setEnabled(True)
                    self.setskipsplithotkeyButton.setEnabled(True)
                    self.setundosplithotkeyButton.setEnabled(True)
                    return
                    
                    
                QtGui.QApplication.processEvents()
            
            #need to add: press split key
            keyboard.send(str(self.splitLineEdit.text()))
            self.split_image_number=self.split_image_number+1
            if self.number_of_split_images != self.split_image_number:
                self.resetButton.setEnabled(False)
                self.undosplitButton.setEnabled(False)
                self.skipsplitButton.setEnabled(False)
                self.currentSplitImage.setText('none (paused)')
                self.currentSplitImage.setAlignment(QtCore.Qt.AlignCenter)
                QtGui.QApplication.processEvents()
                QtTest.QTest.qWait(self.pauseDoubleSpinBox.value()*1000)
                self.resetButton.setEnabled(True)
                
        
        #loop breaks to here when the last image splits
        self.startautosplitterButton.setText('Start Auto Splitter')   
        self.currentSplitImage.setText(' ')
        self.livesimilarityLabel.setText(' ')
        self.highestsimilarityLabel.setText(' ')
        self.startautosplitterButton.setEnabled(True)
        self.resetButton.setEnabled(False)
        self.undosplitButton.setEnabled(False)
        self.skipsplitButton.setEnabled(False)
        self.setsplithotkeyButton.setEnabled(True)
        self.setresethotkeyButton.setEnabled(True)
        self.setskipsplithotkeyButton.setEnabled(True)
        self.setundosplithotkeyButton.setEnabled(True)

        QtGui.QApplication.processEvents()        
                
        
        
                 
#Widget for dragging screen region   
class SelectRegionWidget(QtGui.QWidget):
    def __init__(self):
        super(SelectRegionWidget,self).__init__()        
        root = tk.Tk()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
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

        
def main():
    global app
    app = QtGui.QApplication(sys.argv)
    w = AutoSplit()
    w.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()