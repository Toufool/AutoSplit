import sys
import os
import pymouse
import time
import numpy as np
import mss
import pyautogui
import pythoncom as pc, pyHook as ph
from PIL import Image
from PIL import ImageChops
from PyQt4 import QtGui, QtCore
from PyQt4 import QtTest

#initial values
split_image_directory='No Folder Selected'
x1='none'
y1='none'
x2='none'
y2='none'
split_hotkey='none'
reset_hotkey='none'
undo_split_hotkey='none'
skip_split_hotkey='none'
mean_percent_diff=100
mean_percent_diff_threshold=10
pause=10



class Window(QtGui.QMainWindow):
    
    def __init__(self):
        global app
        super(Window, self).__init__()
        self.setFixedSize(430,460)
        self.setWindowTitle("Auto Splitter")
        self.statusBar()
        self.home()
        app.aboutToQuit.connect(self.closeEvent)
        
    #all buttons, labels, lineedits in the window.
    def home(self):
        global split_image_directory
        global split_image_path
        global x1,y1,x2,y2
        global mean_percent_diff_threshold
        global FilePathLine
        global TopLeftLabel
        global TopLeftButton
        global BottomRightLabel
        global BottomRightButton
        global split_hotkey
        global reset_hotkey
        global undo_split_hotkey
        global skip_split_hotkey
        global SplitHotkeyLine
        global ResetHotkeyLine
        global CheckFPSLabel
        global CheckFPSButton
        global CurrentSplitImageLabel2
        global StartAutoSplitterButton
        global SplitHotkeyButton
        global ResetHotkeyButton
        global BrowseButton
        global ShowLivePercentDifferenceLabel
        global CheckBox
        global UndoHotkeyButton
        global UndoHotkeyLine
        global UndoHotkeyLabel
        global SkipHotkeyButton
        global SkipHotkeyLine
        global SkipHotkeyLabel
        global ThresholdDropdown
        global PauseDropdown
        global current_split_image
        global ResetButton
        global UndoButton
        global SkipButton
        #SPLIT IMAGE FOLDER
        
        
        FilePathLabel=QtGui.QLabel('Split Image Folder:', self)
        FilePathLabel.move(10,20)
        
        FilePathLine=QtGui.QLineEdit(split_image_directory,self)
        FilePathLine.move(110,23)
        FilePathLine.resize(200,25)
        FilePathLine.setReadOnly(True)
        
        BrowseButton = QtGui.QPushButton("Browse..",self)
        BrowseButton.clicked.connect(self.browse)
        BrowseButton.move(320,20)
        
        #GAME REGION
        
        GameRegionLabel=QtGui.QLabel('------------------ Game Screen Region --------------------', self)
        GameRegionLabel.move(93,60)
        GameRegionLabel.resize(250,30)
        
        TopLeftLabel=QtGui.QLabel('Top Left Coordinates:'+'                         '+x1+', '+y1, self)
        TopLeftLabel.move(10,90)
        TopLeftLabel.resize(250,20)
        
        TopLeftButton=QtGui.QPushButton("Set Top Left",self)
        TopLeftButton.clicked.connect(self.set_top_left)
        TopLeftButton.move(320,90)
        TopLeftButton.resize(100,20)
        
        BottomRightLabel=QtGui.QLabel('Bottom Right Coordinates:'+'                 '+x2+', '+y2, self)
        BottomRightLabel.move(10,110)
        BottomRightLabel.resize(250,20)
        
        BottomRightButton=QtGui.QPushButton("Set Bottom Right",self)
        BottomRightButton.clicked.connect(self.set_bottom_right)
        BottomRightButton.move(320,110)
        BottomRightButton.resize(100,20)
        
        #HOTKEYS
        
        #initiate HookKeyboard from pyHook
        hm = ph.HookManager()
        hm.KeyDown = self.hotkey
        hm.HookKeyboard()
        
        HotkeysLabel=QtGui.QLabel('----------------- Timer Global Hotkeys ----------------------', self)
        HotkeysLabel.move(94,140)
        HotkeysLabel.resize(250,30)
        
        SplitHotkeyLabel=QtGui.QLabel('Split:', self)
        SplitHotkeyLabel.move(10,165)
        
        SplitHotkeyLine=QtGui.QLineEdit(split_hotkey,self)
        SplitHotkeyLine.move(167,170)
        SplitHotkeyLine.resize(95,20)
        SplitHotkeyLine.setReadOnly(True)
        
        SplitHotkeyButton=QtGui.QPushButton("Set Hotkey",self)
        SplitHotkeyButton.clicked.connect(self.set_split_hotkey)
        SplitHotkeyButton.move(320,170)
        SplitHotkeyButton.resize(100,20)
        
        ResetHotkeyLabel=QtGui.QLabel('Reset (optional):', self)
        ResetHotkeyLabel.move(10,190)
        
        ResetHotkeyLine=QtGui.QLineEdit(reset_hotkey,self)
        ResetHotkeyLine.move(167,195)
        ResetHotkeyLine.resize(95,20)
        ResetHotkeyLine.setReadOnly(True)
        
        ResetHotkeyButton=QtGui.QPushButton("Set Hotkey",self)
        ResetHotkeyButton.clicked.connect(self.set_reset_hotkey)
        ResetHotkeyButton.move(320,195)
        ResetHotkeyButton.resize(100,20)
        
        UndoHotkeyLabel=QtGui.QLabel('Undo Split (optional):', self)
        UndoHotkeyLabel.move(10,215)
        
        UndoHotkeyLine=QtGui.QLineEdit(undo_split_hotkey,self)
        UndoHotkeyLine.move(167,220)
        UndoHotkeyLine.resize(95,20)
        UndoHotkeyLine.setReadOnly(True)
        
        UndoHotkeyButton=QtGui.QPushButton("Set Hotkey",self)
        UndoHotkeyButton.clicked.connect(self.set_undo_split_hotkey)
        UndoHotkeyButton.move(320,220)
        UndoHotkeyButton.resize(100,20)
        
        SkipHotkeyLabel=QtGui.QLabel('Skip Split (optional):', self)
        SkipHotkeyLabel.move(10,240)
        
        SkipHotkeyLine=QtGui.QLineEdit(skip_split_hotkey,self)
        SkipHotkeyLine.move(167,245)
        SkipHotkeyLine.resize(95,20)
        SkipHotkeyLine.setReadOnly(True)
        
        SkipHotkeyButton=QtGui.QPushButton("Set Hotkey",self)
        SkipHotkeyButton.clicked.connect(self.set_skip_split_hotkey)
        SkipHotkeyButton.move(320,245)
        SkipHotkeyButton.resize(100,20)
        
        #OPTIONS
        
        OptionsLabel=QtGui.QLabel('------------------------- Options -------------------------', self)
        OptionsLabel.move(93,280)
        OptionsLabel.resize(250,30)
        
        StartAutoSplitterButton=QtGui.QPushButton("Start Auto Splitter",self)
        StartAutoSplitterButton.clicked.connect(self.auto_splitter)
        StartAutoSplitterButton.move(320,420)
        StartAutoSplitterButton.resize(100,30)
        
        CheckFPSButton=QtGui.QPushButton("Check FPS",self)
        CheckFPSButton.clicked.connect(self.check_fps)
        CheckFPSButton.move(320,310)
        CheckFPSButton.resize(100,25)
        
        CheckFPSLabel=QtGui.QLabel('FPS:   ', self)
        CheckFPSLabel.move(257,312)
        CheckFPSLabel.resize(50,20)
        
        CurrentSplitImageLabel=QtGui.QLabel('Current Split Image:', self)
        CurrentSplitImageLabel.move(10,380)
        CurrentSplitImageLabel.resize(300,20)
        
        CurrentSplitImageLabel2=QtGui.QLabel('', self)
        CurrentSplitImageLabel2.move(10,395)
        CurrentSplitImageLabel2.resize(135,20)
        
        ShowLivePercentDifferenceLabel=QtGui.QLabel('', self)
        ShowLivePercentDifferenceLabel.move(257,335)
        
        CheckBox=QtGui.QCheckBox('Show Live % Match',self)
        CheckBox.move(305,335)
        CheckBox.resize(270,30)
        CheckBox.stateChanged.connect(self.show_live_percent_difference)
        
        ThresholdDropdownLabel=QtGui.QLabel("% Match Threshold:",self)
        ThresholdDropdownLabel.move(10,335)
        ThresholdDropdownLabel.resize(150,30)
        
        ThresholdDropdown=QtGui.QComboBox(self)
        ThresholdDropdown.move(130,340)
        ThresholdDropdown.resize(70,20)
        ThresholdDropdown.addItem("test")
        ThresholdDropdown.addItem("95%")
        ThresholdDropdown.addItem("94%")
        ThresholdDropdown.addItem("93%")
        ThresholdDropdown.addItem("92%")
        ThresholdDropdown.addItem("91%")
        ThresholdDropdown.addItem("90%")
        ThresholdDropdown.addItem("89%")
        ThresholdDropdown.addItem("88%")
        ThresholdDropdown.addItem("87%")
        ThresholdDropdown.addItem("86%")
        ThresholdDropdown.addItem("85%")
        ThresholdDropdown.setCurrentIndex(6)
        ThresholdDropdown.activated[str].connect(self.threshold)
        
        PauseLabel=QtGui.QLabel("Pause after split for:",self)
        PauseLabel.move(10,310)
        PauseLabel.resize(150,30)
        
        PauseDropdown=QtGui.QComboBox(self)
        PauseDropdown.move(130,315)
        PauseDropdown.resize(70,20)
        PauseDropdown.addItem("10 sec")
        PauseDropdown.addItem("20 sec")
        PauseDropdown.addItem("30 sec")
        PauseDropdown.addItem("40 sec")
        PauseDropdown.addItem("50 sec")
        PauseDropdown.addItem("60 sec")
        PauseDropdown.addItem("70 sec")
        PauseDropdown.addItem("80 sec")
        PauseDropdown.addItem("90 sec")
        PauseDropdown.addItem("100 sec")
        PauseDropdown.addItem("110 sec")
        PauseDropdown.addItem("120 sec")
        PauseDropdown.activated[str].connect(self.pause)
        
        ResetButton=QtGui.QPushButton("Reset",self)
        ResetButton.clicked.connect(self.reset)
        ResetButton.move(320,390)
        ResetButton.resize(100,25)
        ResetButton.setEnabled(False)
        
        UndoButton=QtGui.QPushButton("Undo Split",self)
        UndoButton.clicked.connect(self.undo_split)
        UndoButton.move(15,422)
        UndoButton.resize(60,25)
        UndoButton.setEnabled(False)
        
        SkipButton=QtGui.QPushButton("Skip Split",self)
        SkipButton.clicked.connect(self.skip_split)
        SkipButton.move(75,422)
        SkipButton.resize(60,25)
        SkipButton.setEnabled(False)
        
        current_split_image = QtGui.QLabel('no current image',self)
        current_split_image.setAlignment(QtCore.Qt.AlignCenter)
        current_split_image.resize(120,80)
        current_split_image.move(155,370)
        
        self.show()
    
    #displays the current split image
    def set_current_split_image(self):
        global current_split_image
        global split_image_path
        pixmap = QtGui.QPixmap(split_image_path)
        current_split_image.setPixmap(pixmap.scaled(current_split_image.size()))
    
    #displays no image for current split image
    def set_no_current_split_image(self):
        global current_split_image
        current_split_image.setText('no current image')
        current_split_image.setAlignment(QtCore.Qt.AlignCenter)
    
    #get split image directory from user from clicking browse..
    def browse(self):
        global split_image_directory
        split_image_directory = str(QtGui.QFileDialog.getExistingDirectory(self, "Select Split Image Directory"))+'\\'
        FilePathLine.setText(split_image_directory)
    
    #activate when using match% threshold dropdown
    def threshold(self, text):
        global mean_percent_diff_threshold
        if text == 'test':
            mean_percent_diff_threshold=-1 #putting this to -1 just makes it so that auto_splitter will never split, so that the user can test their splits.
        else:
            mean_percent_diff_threshold=100-int(text[:-1]) #this flips match % different threshold text from the dropdown to a mean_percent_diff_threshold int
    
    #activates when using pause dropdown
    def pause(self,text):
        global pause
        pause = int(text[:-4]) #changes text from pause dropdown to an int to pause after a split
    
            
    def show_live_percent_difference(self, state):
            if state == QtCore.Qt.Checked:
                ShowLivePercentDifferenceLabel.setText('n/a')
            else:
                ShowLivePercentDifferenceLabel.setText(str(''))
    
    #activates when pressing set top left button, hover mouse over top left of game screen. 5 seconds to do so
    def set_top_left(self):
        global x1,y1
        self.disable_buttons()
        i=5
        while i > 0:
            TopLeftButton.setText(str(i)+'..')
            QtGui.QApplication.processEvents()
            time.sleep(1)
            i=i-1
        mouse = pymouse.PyMouse()
        top_left=(mouse.position())
        top_left=np.asarray(top_left)
        x1,y1=top_left
        x1,y1=int(x1),int(y1)
        TopLeftLabel.setText('Top Left Coordinates:'+'                         '+str(x1)+', '+str(y1))
        TopLeftButton.setText('Set Top Left')
        self.enable_buttons()
    
    #activates when pressing set bottom right button, hover mouse over bottom right of game screen. 5 seconds to do so
    def set_bottom_right(self):
        global x2,y2
        self.disable_buttons()
        i=5
        while i > 0:
            BottomRightButton.setText(str(i)+'..')
            QtGui.QApplication.processEvents()
            time.sleep(1)
            i=i-1
        mouse = pymouse.PyMouse()
        bottom_right=(mouse.position())
        bottom_right=np.asarray(bottom_right)
        x2,y2=bottom_right
        x2,y2=int(x2),int(y2)
        BottomRightLabel.setText('Bottom Right Coordinates:'+'                 '+str(x2)+', '+str(y2))
        BottomRightButton.setText('Set Bottom Right')
        self.enable_buttons()
    
    #setting global hotkeys and doing things when they are hit
    def hotkey(self,event):
        global split_hotkey
        global old_split_hotkey
        global reset_hotkey
        global old_reset_hotkey
        global undo_split_hotkey
        global old_undo_split_hotkey
        global skip_split_hotkey
        global old_skip_split_hotkey
        #set split hotkey
        if SplitHotkeyButton.text() == 'press a key...':
            old_split_hotkey=split_hotkey
            while old_split_hotkey == split_hotkey:
                pc.PumpWaitingMessages()
                split_hotkey=event.Key
                if old_split_hotkey == split_hotkey:
                    SplitHotkeyLine.setText(split_hotkey)
                    SplitHotkeyButton.setText('Set Hotkey')
                    self.enable_buttons()
                    return
                else:
                    SplitHotkeyLine.setText(split_hotkey)
                    SplitHotkeyButton.setText('Set Hotkey')
                    self.enable_buttons()
                    return
        #set reset hotkey
        if ResetHotkeyButton.text() == 'press a key...':
            old_reset_hotkey=reset_hotkey
            while old_reset_hotkey == reset_hotkey:
                pc.PumpWaitingMessages()
                reset_hotkey=event.Key
                if old_reset_hotkey == reset_hotkey:
                    ResetHotkeyLine.setText(reset_hotkey)
                    ResetHotkeyButton.setText('Set Hotkey')
                    self.enable_buttons()
                    return
                else:  
                    ResetHotkeyLine.setText(reset_hotkey)
                    ResetHotkeyButton.setText('Set Hotkey')
                    self.enable_buttons()
                    return
        #set undo split hotkey
        if UndoHotkeyButton.text() == 'press a key...':
            old_undo_split_hotkey=undo_split_hotkey
            while old_undo_split_hotkey == undo_split_hotkey:
                pc.PumpWaitingMessages()
                undo_split_hotkey=event.Key
                if old_undo_split_hotkey == undo_split_hotkey:
                    UndoHotkeyLine.setText(undo_split_hotkey)
                    UndoHotkeyButton.setText('Set Hotkey')
                    self.enable_buttons()
                    return
                else:  
                    UndoHotkeyLine.setText(undo_split_hotkey)
                    UndoHotkeyButton.setText('Set Hotkey')
                    self.enable_buttons()
                    return
        #set skip split hotkey
        if SkipHotkeyButton.text() == 'press a key...':
            old_skip_split_hotkey=skip_split_hotkey
            while old_skip_split_hotkey == skip_split_hotkey:
                pc.PumpWaitingMessages()
                skip_split_hotkey=event.Key
                if old_skip_split_hotkey == skip_split_hotkey:
                    SkipHotkeyLine.setText(skip_split_hotkey)
                    SkipHotkeyButton.setText('Set Hotkey')
                    self.enable_buttons()
                    return
                else:  
                    SkipHotkeyLine.setText(undo_split_hotkey)
                    SkipHotkeyButton.setText('Set Hotkey')
                    self.enable_buttons()
                    return
        #check for hotkey hits when auto splitter is running
        if StartAutoSplitterButton.text() == 'Running..':
            pc.PumpWaitingMessages()
            key = event.Key
            if key == reset_hotkey:
                self.reset()
            if key == undo_split_hotkey:
                self.undo_split()
            if key == skip_split_hotkey:
                self.skip_split()
                    
    
    def set_split_hotkey(self):
        self.disable_buttons()
        SplitHotkeyButton.setText('press a key...')
        QtGui.QApplication.processEvents()
    def set_reset_hotkey(self):
        self.disable_buttons()
        ResetHotkeyButton.setText('press a key...')
        QtGui.QApplication.processEvents()
    def set_undo_split_hotkey(self):
        self.disable_buttons()
        UndoHotkeyButton.setText('press a key...')
        QtGui.QApplication.processEvents()
    def set_skip_split_hotkey(self):
        self.disable_buttons()
        SkipHotkeyButton.setText('press a key...')
        QtGui.QApplication.processEvents()
    
    #activates from either a hotkey or the reset button
    def reset(self):
        global StartAutoSplitterButton
        global ShowLivePercentDifferenceLabel
        global CurrentSplitImageLabel2
        global split_image_number
        global reset_hotkey
        StartAutoSplitterButton.setText('Start Auto Splitter')
        ShowLivePercentDifferenceLabel.setText('n/a')
        CurrentSplitImageLabel2.setText('')
        self.set_no_current_split_image()
        self.enable_buttons()
        ResetButton.setEnabled(False)
        UndoButton.setEnabled(False)
        SkipButton.setEnabled(False)
    
    #activates from either a hotkey or undo split button
    def undo_split(self):
        global split_image_number
        global split_image_file
        global split_image_path
        global split_image
        global split_image_resized
        global CurrentSplitImageLabel2
        global undo_split_hotkey
        
        if split_image_number == 0:
            split_image_number=split_image_number
        else:
            pyautogui.press(undo_split_hotkey)
            split_image_number = split_image_number-1
            split_image_file=os.listdir(split_image_directory)[0+split_image_number]
            split_image_path=split_image_directory+split_image_file
            split_image = Image.open(split_image_path)
            split_image = split_image.convert('RGB')
            split_image_resized=split_image.resize((120,90))
            CurrentSplitImageLabel2.setText(split_image_file)
            self.set_current_split_image()
            QtGui.QApplication.processEvents()
            time.sleep(0.2)
    
    #activates when a hotkey is split or from skip split button   
    def skip_split(self):
        global split_image_number
        global number_of_split_images
        global split_image_file
        global split_image_path
        global split_image
        global split_image_resized
        global CurrentSplitImageLabel2
        global skip_split_hotkey
        
        if split_image_number == number_of_split_images-1:
            split_image_number=split_image_number
        else:
            pyautogui.press(skip_split_hotkey)
            split_image_number = split_image_number+1
            split_image_file=os.listdir(split_image_directory)[0+split_image_number]
            split_image_path=split_image_directory+split_image_file
            split_image = Image.open(split_image_path)
            split_image = split_image.convert('RGB')
            split_image_resized=split_image.resize((120,90)) #turn split image into 120x90 image
            CurrentSplitImageLabel2.setText(split_image_file)
            self.set_current_split_image()
            QtGui.QApplication.processEvents()
            time.sleep(0.2)
    
    def disable_buttons(self):
        BrowseButton.setEnabled(False)
        TopLeftButton.setEnabled(False)
        BottomRightButton.setEnabled(False)
        SplitHotkeyButton.setEnabled(False)
        ResetHotkeyButton.setEnabled(False)
        UndoHotkeyButton.setEnabled(False)
        SkipHotkeyButton.setEnabled(False)
        CheckFPSButton.setEnabled(False)
        StartAutoSplitterButton.setEnabled(False)
        ThresholdDropdown.setEnabled(False)
        PauseDropdown.setEnabled(False)
        ResetButton.setEnabled(False)
        
    
    def enable_buttons(self):
        BrowseButton.setEnabled(True)
        TopLeftButton.setEnabled(True)
        BottomRightButton.setEnabled(True)
        SplitHotkeyButton.setEnabled(True)
        ResetHotkeyButton.setEnabled(True)
        UndoHotkeyButton.setEnabled(True)
        SkipHotkeyButton.setEnabled(True)
        CheckFPSButton.setEnabled(True)
        StartAutoSplitterButton.setEnabled(True)
        ThresholdDropdown.setEnabled(True)
        PauseDropdown.setEnabled(True)
        
    def coordinate_error_message(self):
        msgBox = QtGui.QMessageBox()
        msgBox.setText("error: invalid coordinates!")
        msgBox.exec_()
    
    def split_image_directory_error_message(self):
        msgBox = QtGui.QMessageBox()
        msgBox.setText("error: no split image folder found")
        msgBox.exec_()
    
    def split_hotkey_error_message(self):
        msgBox = QtGui.QMessageBox()
        msgBox.setText("set your split hotkey!")
        msgBox.exec_()
    
    def image_type_error(self):
        msgBox = QtGui.QMessageBox()
        msgBox.setText("error: all images must be PNG type")
        msgBox.exec_()
    
    #closes entire process when you close the program
    def closeEvent(self, app):
        sys.exit()
    
    def check_fps(self):
        global split_image_directory
        global x1,y1,x2,y2
        global split_hotkey
        global reset_hotkey
        global FPS
        if split_image_directory == 'No Folder Selected' or split_image_directory == '/':
            self.split_image_directory_error_message()
            return
        if not all(File.endswith(".png") or File.endswith(".PNG") for File in os.listdir(split_image_directory)):
            self.image_type_error()
            return
        if x2 <= x1 or y2 <= y1 or type(x1)==str or type(x2)==str:
            self.coordinate_error_message()
            return
        CheckFPSButton.setText('Calculating...')
        self.disable_buttons()
        QtGui.QApplication.processEvents()
        split_image_file=os.listdir(split_image_directory)[0]
        split_image_path=split_image_directory+split_image_file
        split_image = Image.open(split_image_path)
        split_image = split_image.convert('RGB')
        split_image_resized=split_image.resize((120,90))
        #END SPLIT IMAGE STUFF
            
        bbox=x1,y1,x2,y2
        mean_percent_diff=100
        count=0
        t0=time.time()
        while count <= 100:
            with mss.mss() as sct:
                QtGui.QApplication.processEvents()
                sct_img = sct.grab(bbox)
                game_image = Image.frombytes('RGB', sct_img.size, sct_img.rgb)
                game_image_resized = game_image.resize((120,90))
                diff=ImageChops.difference(split_image_resized,game_image_resized)
                diff_pix_val=np.asarray(list(diff.getdata()))
                percent_diff=diff_pix_val/255.*100.
                mean_percent_diff=np.mean(percent_diff)
                count=count+1
        t1 = time.time()
        FPS=int(100/(t1-t0))
        FPS=str(FPS)
        CheckFPSLabel.setText('FPS: '+FPS)
        CheckFPSButton.setText('Check FPS')
        self.enable_buttons()
        return
    
    def auto_splitter(self):
        global split_image_directory
        global split_image_file
        global x1,y1,x2,y2
        global split_hotkey
        global reset_hotkey
        global undo_split_hotkey
        global skip_split_hotkey
        global split_image_number
        global number_of_split_images
        global split_image_file
        global split_image_path
        global split_image
        global split_image_resized
        global CurrentSplitImageLabel2
        global mean_percent_diff
        global mean_percent_diff_threshold
        global pause
        global current_split_image
        global StartAutoSplitterButton
       
        #multiple checks to see if an error message needs to display
        if split_image_directory == 'No Folder Selected' or split_image_directory == '/':
            self.split_image_directory_error_message()
            return
        if x2 <= x1 or y2 <= y1 or type(x1)==str or type(x2)==str:
            self.coordinate_error_message()
            return
        if split_hotkey == 'none':
            self.split_hotkey_error_message()
            return
        if not all(File.endswith(".png") or File.endswith(".PNG") for File in os.listdir(split_image_directory)):
            self.image_type_error()
            return
        
        #disable buttons, set button text, start timer, get number of split images in the folder.
        self.disable_buttons()
        ResetButton.setEnabled(True)
        UndoButton.setEnabled(True)
        SkipButton.setEnabled(True)
        
        StartAutoSplitterButton.setText('Running..')
        QtGui.QApplication.processEvents()
        pyautogui.press(split_hotkey)
        number_of_split_images=len(os.listdir(split_image_directory))
        
        #grab split image from folder, resize, and set current split image text
        split_image_number=0
        while split_image_number < number_of_split_images:
            split_image_file=os.listdir(split_image_directory)[0+split_image_number]
            split_image_path=split_image_directory+split_image_file
            split_image = Image.open(split_image_path)
            split_image = split_image.convert('RGB')
            split_image_resized=split_image.resize((120,90)) #turn split image into 120x90 image
            CurrentSplitImageLabel2.setText(split_image_file)
            self.set_current_split_image()
            QtGui.QApplication.processEvents()

            #while loop: constantly take screenshot of user-defined area, resize, and compare to split image. if the images meet the user-defined match threshold, exit while loop and split.
            bbox=x1,y1,x2,y2
            mean_percent_diff=100
            while mean_percent_diff > mean_percent_diff_threshold:
                with mss.mss() as sct:
                    QtGui.QApplication.processEvents()
                    sct_img = sct.grab(bbox)
                    game_image = Image.frombytes('RGB', sct_img.size, sct_img.rgb)
                    game_image_resized = game_image.resize((120,90))
                    diff=ImageChops.difference(split_image_resized,game_image_resized)
                    diff_pix_val=np.asarray(list(diff.getdata()))
                    percent_diff=diff_pix_val/255.*100.
                    mean_percent_diff=np.mean(percent_diff)
                    #if checkbox is checked, show live percent difference to a few decimal places.
                    if CheckBox.isChecked():
                        ShowLivePercentDifferenceLabel.setText(str(100-mean_percent_diff)[0:5]+'%')
                        QtGui.QApplication.processEvents()
                    #if the auto splitter buttons text is changed back to start auto splitter, we know that reset button was pressed, so return
                    if StartAutoSplitterButton.text() == 'Start Auto Splitter':
                        return
            
            #loop breaks to here when match threshold is met. splits the timer, goes to next split, and pauses for a user-defined amount of time before comparing the next split.
            pyautogui.press(split_hotkey)
            split_image_number=split_image_number+1
            if number_of_split_images != split_image_number:
                current_split_image.setText('none (paused)')
                CurrentSplitImageLabel2.setText('none (paused)')
                QtGui.QApplication.processEvents()
                QtTest.QTest.qWait(pause*1000)
                
        #loop breaks to here when the last image splits. 
        self.set_no_current_split_image()
        CurrentSplitImageLabel2.setText('')
        StartAutoSplitterButton.setText('Start Auto Splitter')
        self.enable_buttons()
        QtGui.QApplication.processEvents()
    
def run():
    global app
    app = QtGui.QApplication(sys.argv)
    GUI = Window()
    sys.exit(app.exec_())

run()
