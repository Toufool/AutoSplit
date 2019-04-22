# <img src="https://raw.githubusercontent.com/austinryan/Auto-Split/master/icon.ico" alt="LiveSplit" height="42" width="45" align="top"/> AutoSplit</h1>

This program compares split images to a capture region of any window (OBS, xsplit, etc.) and automatically hits your split hotkey when there is a match. It can be used in tandem with any speedrun timer that accepts hotkeys (LiveSplit, wsplit, etc.). The purpose of this program is to remove the need to manually press your split hotkey and also increase the accuracy of your splits. 

<p align="center">
  <img src="https://github.com/austinryan/Auto-Split/blob/master/example.gif?raw=true" />
</p>

# TUTORIAL

## DOWNLOAD AND OPEN

### Compatability
- Windows 7 and 10.

### Opening the program
- Download the [latest version](https://github.com/austinryan/Auto-Split/releases)
- Extract the file and open AutoSplit.exe.

## SPLIT IMAGE FOLDER
- Supported image file types: .png, .jpg, .jpeg, .bmp, and [more](https://docs.opencv.org/3.0-beta/modules/imgcodecs/doc/reading_and_writing_images.html#imread).
- Images can be any size.
- Recommended filenaming convention: `001_SplitName.png, 002_SplitName.png, 003_SplitName.png`... 
- Custom split image settings are handled in the filename. See how [here](https://github.com/Toufool/Auto-Split#custom-split-image-settings)

## CAPTURE REGION
- Click "Select Region"
- Click and drag to form a rectangle over the region you want to capture.
- Adjust the x, y, width, and height of the capture region manually to make adjustments as needed.
- You can freely move the window that the program is capturing, but resizing the window will cause the capture region to change.
- Once you are happy with your capture region, you may unselect Live Capture Region to decrease CPU usage if you wish.
- You can save a screenshot of the capture region to your split image folder using the Take Screenshot button.

## Max FPS
  - Calculates the maximum comparison rate of the capture region to split images. This value will likely be much higher than needed, so it is highly recommended to limit your FPS depending on the frame rate of the game you are capturing.

## OPTIONS

### Comparison Method
- There are three comparison methods to choose from: L2 Norm, Histograms, and pHash.
  - L2 Norm: This method finds the difference between each pixel, squares it, and sums it over the entire image and takes the square root. This is very fast but is a problem if your image is high frequency. Any translational movement or rotation can cause similarity to be very different.
  - Histograms: An explanation on Histograms comparison can be found [here](https://mpatacchiola.github.io/blog/2016/11/12/the-simplest-classifier-histogram-intersection.html)
  - pHash: An explanation on pHash comparison can be found [here](http://www.hackerfactor.com/blog/index.php?/archives/432-Looks-Like-It.html)
- Note: v1.0.0 used L2 Norm.

### Show Live Similarity
- Displays the live similarity between the capture region and your split image. This number is between 0 and 1, with 1 being a perfect match.

### Show Highest Similarity
- Shows the highest similarity between the capture region and current split image.

### Similarity Threshold
- When the live similarity goes above this value, the program hits your split hotkey and moves to the next split image.

### Pause Time
- Time in seconds that the program stops comparison after a split. Useful for if you have two of the same split images in a row and want to avoid double-splitting. Also useful for reducing CPU usage.

### Custom Split Image Settings
- Each split image can have different thresholds, pause times, and can be flagged.
- These settings are handled in the image's filename. 
- Custom thresholds are place between parenthesis `()` in the filename and the custom thresholds checkbox must be checked. All images must have a custom threshold if the box is checked
- Custom pause times are placed between square brackets `[]` in the filename and the custom pause times checkbox must be checked. All images must have a custom threshold if the box is checked. 
- Flags are placed between curly brackets `{}` in the filename. Multiple flags are placed in the same set of curly brackets `{}`. Current available flags:
  - {d} dummy split. When matched, it moves to the next image without hitting your split hokey.
- Filename example: `001_SplitName_(0.9)_[10].png` is a split image with a threshold of 0.9 and a pause time of 10 seconds.

### Timer Global Hotkeys
- Click "Set Hotkey" on each hotkey to set the hotkeys to AutoSplit. Start / Split hotkey must be the same as the one used in your preferred timer program in order for the splitting to work properly.
- Make sure that Global Hotkeys are enabled in your speedrun timer.
- Skip and Undo Split has a 0.1 second delay for double-tap prevention.
- All of these actions can also be handled by their corresponding buttons.

## Known Limitations
- Transparency in an image is not seen as a mask or "nothing." It gets transformed into solid white.
- Starting your timer/AutoSplit is still manual.
- For many games, it will be difficult to find a split image for the last split of the run.
- The window of the capture region cannot be minimized.

## Known Issues
- When setting your region, you may only see a black image. This is caused by hardware acceleration. You may be able to disable this through the application itself like in [Google Chrome](https://www.technize.net/google-chrome-disable-hardware-acceleration/). If not, this can also be disabled through [Windows](https://www.thewindowsclub.com/hardware-acceleration-windows-7). NOTE: If you notice any computer performance issues after disabling hardware acceleration, re-enable it.
- Using numpad number keys when numlock is on does not split correctly. Either avoid using numpad or turn numlock off to avoid this issue.

## Resources
- Still need help? [Open an issue](https://github.com/Toufool/Auto-Split/issues)
- Join the [AutoSplit Discord](https://discord.gg/Qcbxv9y)


### Credits
- https://github.com/harupy/ for the snipping tool code that I used to integrate into the autosplitter.
- [amaringos](https://twitter.com/amaringos) for the icon.
- [ZanasoBayncuh](https://twitter.com/ZanasoBayncuh) for motivating me to start this project back up and for all of the time spent testing and suggesting improvements.
- Created by [Toufool](https://twitter.com/Toufool) and [Faschz](https://twitter.com/faschz).
