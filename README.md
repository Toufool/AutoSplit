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
- All files in the folder must be .png files
- Images can be any size
- Name split images alphanumerically in the order you want them to split - an easy way to do this is name the files a_splitname.png, b_splitname.png, etc.
- Be mindful of false positives. For example, if you use a black screen for a split image, make sure a black screen will not show up before you want to split (for example, in Super Mario 64, a black loading screen appears after a star, but will also appear if you die).

## CAPTURE REGION
- Click "Select Region"
- Click and drag to form a rectangle over the region you want to capture
- Adjust position, height, and width manually to make slight corrections to the capture region
- You can freely move the window that the program is capturing, but resizing the window will cause the capture region to change
- Once you are happy with your capture region, you may unselect Live Capture Region to decrease CPU usage if you wish
note: Closing the window that the program is capturing will throw and error and reset the auto splitter if it is running

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

### Known Limitations
- Only one region can be used. Searching for sub regions inside the capture region and or image masking may be implemented in the future
- Transparency in an image is not seen as a mask or "nothing." It gets transformed into solid white.
- Starting the timer/auto splitter is still manual
- For many games, it will be difficult to find a split image for the last split of the run
- Similarity threshold cannot be customized per split image
- While the potential is there, load time removal is not the main focus of this program and is not currently implemented


### Credits
https://github.com/harupy/ for the snipping tool code that I used to integrate into the autosplitter.
