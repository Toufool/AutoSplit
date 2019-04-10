# AutoSplit
This program compares split images to a capture region of any window (OBS, xsplit, etc.) and automatically hits your split hotkey when there is a match. It can be used in tandem with any speedrun timer that accepts hotkeys (LiveSplit, wsplit, etc.). The purpose of this program is to remove the need to manually press your split hotkey and also increase the accuracy of your splits. 

<p align="center">
  <img src="https://i.imgur.com/NVHY3g7.png" />
</p>

# TUTORIAL

## DOWNLOAD AND OPEN

### Compatability
- Windows 7 and 10

### Opening the program
- Download the latest version: (no release yet)
- Extract the file and open AutoSplit.exe

## SPLIT IMAGE FOLDER
- Supported image file types: .png, .jpg, .jpeg, .bmp, and more [here](https://docs.opencv.org/3.0-beta/modules/imgcodecs/doc/reading_and_writing_images.html#imread)
- Images can be any size
- Name split images alphanumerically in the order you want them to split - an easy way to do this is name the files a_splitname.png, b_splitname.png, etc.
- Be mindful of false positives. For example, if you use a black screen for a split image, make sure a black screen will not show up before you want to split (for example, in Super Mario 64, a black loading screen appears after a star, but will also appear if you die).

## CAPTURE REGION
- Click "Select Region"
- Click and drag to form a rectangle over the region you want to capture
- Adjust position, height, and width manually to make slight corrections to the capture region
- You can freely move the window that the program is capturing, but resizing the window will cause the capture region to change
- Once you are happy with your capture region, you may unselect Live Capture Region to decrease CPU usage if you wish

## OPTIONS
### Show Live Similarity
- Shows the live similarity between the capture region and your split image. This number is between 0 and 1, with 1 being a perfect match.

### Show Highest Similarity
- Shows the highest similarity between the capture region and current split image.

### Similarity Threshold
- When the live similarity goes above this value, the program hits your split hotkey and moves to the next split image. A good starting point is 0.9.

### Pause Time
- Time in seconds that the program stops comparison after a split. Useful for if you have two of the same split images in a row and want to avoid double-splitting. Also useful for reducing CPU usage.

### Check Max FPS
- Calculates the maximum comparison rate of the capture region to split images. This value will likely be much higher than needed, so it is highly recommended to limit your FPS depending on the frame rate of the game you are capturing.

### Timer Global Hotkeys
- Click "Set Hotkey" on each option and make sure that they match up to what your hotkeys are in your preferred speedrun timer. These are global hotkeys and act the same as they do in livesplit, wsplit, etc. They will work even when the program is minimized.

## Known Limitations
- There are currently no custom settings for each split image (threshold, pause time, sub-regions etc.)
- Transparency in an image is not seen as a mask or "nothing." It gets transformed into solid white
- Starting your timer/AutoSplit is still manual
- For many games, it will be difficult to find a split image for the last split of the run

## Known Issues
- When setting your region, you may only see a black image. This is caused by hardware acceleration. You may be able to disable this through the application itself like in [Google Chrome](https://www.technipages.com/google-chrome-enable-disable-hardware-acceleration-mode). If not, this can also be disabled through [Windows](https://www.thewindowsclub.com/hardware-acceleration-windows-7). If you do not see the "troubleshoot" tab or it is grayed out, you can disable hardware acceleration through registry via method 2 on [this page](https://appuals.com/disable-hardware-acceleration-windows-7-8-8-1-10/). NOTE: If you notice any computer performance issues after disabling hardware acceleration, re-enable it. If you disabled through registry, delete the DWORD key that you created.

### Credits
https://github.com/harupy/ for the snipping tool code that I used to integrate into the autosplitter.
