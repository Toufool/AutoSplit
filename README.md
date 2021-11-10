# <img src="https://raw.githubusercontent.com/austinryan/Auto-Split/master/icon.ico" alt="LiveSplit" height="42" width="45" align="top"/> AutoSplit</h1>

This program compares split images to a capture region of any window (OBS, xsplit, etc.) and automatically hits your split hotkey when there is a match. It can be used in tandem with any speedrun timer that accepts hotkeys (LiveSplit, wsplit, etc.). The purpose of this program is to remove the need to manually press your split hotkey and also increase the accuracy of your splits. 

<p align="center">
  <img src="https://github.com/austinryan/Auto-Split/blob/master/example1.5.0.gif" />
</p>

# TUTORIAL

## DOWNLOAD AND OPEN

### Compatability
- Windows 7, 10, and 11

### Building
- Read [requirements.txt](/requirements.txt) for information on how to run/build the python code

### Opening the program
- Download the [latest version](https://github.com/austinryan/Auto-Split/releases)
- Extract the file and open AutoSplit.exe.

### Building
- Read [requirements.txt](/requirements.txt) for information on how to run/build the python code (this is not required for normal use).

## Split Image Folder
- Supported image file types: .png, .jpg, .jpeg, .bmp, and [more](https://docs.opencv.org/3.0-beta/modules/imgcodecs/doc/reading_and_writing_images.html#imread).
- Images can be any size.
- Images are matched in alphanumerical order.
- Recommended filenaming convention: `001_SplitName.png, 002_SplitName.png, 003_SplitName.png`... 
- Custom split image settings are handled in the filename. See how [here](https://github.com/Toufool/Auto-Split#custom-split-image-settings).
- Images can be created using Print Screen, [Snipping Tool](https://support.microsoft.com/en-us/help/4027213/windows-10-open-snipping-tool-and-take-a-screenshot), or AutoSplit's Take Screenshot button.

## Capture Region
- This is the region that your split images are compared to. Usually, this is going to be the full game screen.
- Click "Select Region"
- Click and drag to form a rectangle over the region you want to capture.
- Adjust the x, y, width, and height of the capture region manually to make adjustments as needed.
- If you want to align your capture region by using a reference image, click "Align Region"
- You can freely move the window that the program is capturing, but resizing the window will cause the capture region to change.
- Once you are happy with your capture region, you may unselect Live Capture Region to decrease CPU usage if you wish.
- You can save a screenshot of the capture region to your split image folder using the Take Screenshot button.

## Max FPS
  - Calculates the maximum comparison rate of the capture region to split images. This value will likely be much higher than needed, so it is highly recommended to limit your FPS depending on the frame rate of the game you are capturing.

## OPTIONS

### Comparison Method
- There are three comparison methods to choose from: L2 Norm, Histograms, and pHash.
  - L2 Norm: This method finds the difference between each pixel, squares it, and sums it over the entire image and takes the square root. This is very fast but is a problem if your image is high frequency. Any translational movement or rotation can cause similarity to be very different.
  - Histograms: An explanation on Histograms comparison can be found [here](https://mpatacchiola.github.io/blog/2016/11/12/the-simplest-classifier-histogram-intersection.html). This is a great method to use if you are using several masked images.
  - pHash: An explanation on pHash comparison can be found [here](http://www.hackerfactor.com/blog/index.php?/archives/432-Looks-Like-It.html). It is highly recommended to NOT use pHash if you use masked images. It is very inaccurate.
- Note: v1.0 used L2 Norm.

### Show Live Similarity
- Displays the live similarity between the capture region and the current split image. This number is between 0 and 1, with 1 being a perfect match.

### Show Highest Similarity
- Shows the highest similarity between the capture region and current split image.

### Similarity Threshold
- When the live similarity goes above this value, the program hits your split hotkey and moves to the next split image.

### Pause Time
- Time in seconds that the program stops comparison after a split. Useful for if you have two of the same split images in a row and want to avoid double-splitting. Also useful for reducing CPU usage.

### Delay Time
- Time in milliseconds that the program waits before hitting the split hotkey for that specific split.

### Custom Split Image Settings
- Each split image can have different thresholds, pause times, delay split times, loop amounts, and can be flagged.
- These settings are handled in the image's filename. 
- Custom thresholds are place between parenthesis `()` in the filename and the custom thresholds checkbox must be checked. All images must have a custom threshold if the box is checked.
- Custom pause times are placed between square brackets `[]` in the filename and the custom pause times checkbox must be checked. All images must have a custom threshold if the box is checked. 
- Custom delay times are placed between hash signs `##` in the filename. Note that these are in milliseconds. For example, a 10 second split delay would be `#10000#`. You cannot skip or undo splits during split delays.
- Image loop amounts are placed between at symbols `@@` in the filename. For example, a specific image that you want to split 5 times in a row would be `@5@`. The current loop # is conveniently located beneath the current split image.
- Flags are placed between curly brackets `{}` in the filename. Multiple flags are placed in the same set of curly brackets. Current available flags:
  - {d} dummy split image. When matched, it moves to the next image without hitting your split hotkey.
  - {b} split when similarity goes below the threshold rather than above. When a split image filename has this flag, the split image similarity will go above the threshold, do nothing, and then split the next time the similarity goes below the threshold.
  - {m} masked split image. This allows you to customize what you want compared in your split image by using transparency. Transparent pixels in the split image are ignored when comparing. This is useful if only a certain part of the capture region is consistent (for example, consistent text on the screen, but the background is always different). These images MUST be .png and contain transparency. For more on this, see [How to Create a Masked Image](https://github.com/Toufool/Auto-Split/blob/master/README.md#how-to-create-a-masked-image). Histogram or L2 norm comparison is recommended if you use any masked images. It is highly recommended that you do NOT use pHash comparison if you use any masked images, as it is very inaccurate
  - {p} pause flag. When a split image filename has this flag, it will hit your pause hotkey rather than your split hokey.
  - A pause flag and a dummy flag `{pd}` cannot be used together
- Filename examples: 
  - `001_SplitName_(0.9)_[10].png` is a split image with a threshold of 0.9 and a pause time of 10 seconds.
  - `002_SplitName_(0.9)_[10]_{d}.png` is the second split image with a threshold of 0.9, pause time of 10, and is a dummy split.
  - `003_SplitName_(0.85)_[20]_#3500#_{m}.png` is the third split image with a threshold of 0.85, pause time of 20, delay split time of 3.5 seconds and it is a masked image.
  - `004_SplitName(0.9)_[10]_#3500#_@3@_{b}.png` is the fourth split image with a threshold of 0.9, pause time of 10 seconds, delay split time of 3.5 seconds, will loop 3 times, and will split when similarity is below the threshold rather than above.
  
### How to Create a Masked Image
The best way to create a masked image is to set your capture region as the entire game screen, take a screenshot, and use a program like [paint.net](https://www.getpaint.net/) to "erase" (make transparent) everything you don't want the program to compare. More on how to creating images with transparency using paint.net can be found in [this tutorial](https://www.youtube.com/watch?v=v53kkUYFVn8). The last thing you need to do is add {m} to the filename. For visualization, here is what the capture region compared to a masked split image looks like if you would want to split on "Shine Get!" text in Super Mario Sunshine:

<p align="center">
  <img src="https://raw.githubusercontent.com/Toufool/Auto-Split/master/mask_example_image.PNG" />
</p>

### Reset image
You can have one (and only one) image with the keyword `reset` in its name. AutoSplit will press the reset button when it finds this image. This image will only be used for resets and it will not be tied to any split. You can set a probability and pause time for it. A custom threshold MUST be applied to this image. The pause time is the amount of seconds AutoSplit will wait before checking for the reset image once the run starts. Also the image can be masked, for example: `Reset_(0.95)_[10]_{m}.png`.

### Timer Global Hotkeys
- Click "Set Hotkey" on each hotkey to set the hotkeys to AutoSplit. The Start / Split hotkey and Pause hotkey must be the same as the one used in your preferred timer program in order for the splitting/pausing to work properly.
- Make sure that Global Hotkeys are enabled in your speedrun timer.
- All of these actions can also be handled by their corresponding buttons.
- Note that pressing your Pause Hotkey does not serve any function in AutoSplit itself and is strictly used for the Pause flag.

### Group dummy splits when undoing / skipping
If this option is disabled, AutoSplit will not account for dummy splits when undoing/skipping. Meaning it will cycle through ths splits normally even if they are dummy splits (this was the normal behavior in versions 1.2.0 and older).

If it is enabled, AutoSplit will group dummy splits together with a real split when undoing/skipping. This basically allows you to tie one or more dummy splits to a real split to keep it in sync with LiveSplit/wsplit. 

Examples:
Given these splits: 1 dummy, 2 normal, 3 dummy, 4 dummy, 5 normal, 6 normal.

In this situation you would have only 3 splits in LiveSplit/wsplit (even though there are 6 split images, only 3 are "real" splits). This basically results in 3 groups of splits: 1st split is images 1 and 2. 2nd split is images 3, 4 and 5. 3rd split is image 6.

- If you are in the 1st or 2nd image and press the skip key, it will end up on the 3rd image
- If you are in the 3rd, 4th or 5th image and press the undo key, it will end up on the 1st image
- If you are in the 3rd, 4th or 5th image and press the skip key, it will end up on the 6th image
- If you are in the 6th image and press the undo key, it will end up on the 3rd image

Please note this option cannot currently be used if you have any loop parameter `@@` greater than 1 in any image.

### Loop Split Images
If this option is enabled, when the last split meets the threshold and splits, AutoSplit will loop back to the first split image and continue comparisons.
If this option is disabled, when the last split meets the threshold and splits, AutoSplit will stop running comparisons.
This option does not loop single, specific images. See the Custom Split Image Settings section above for this feature.

### Auto Start On Reset
If this option is enabled, when the reset hotkey is hit, the reset button is pressed, or the reset split image meets its threshold, AutoSplit will reset and automatically start again back at the first split image.
If this option is disabled, when the reset hotkey is hit, the reset button is pressed, or the reset split image meets its threshold, AutoSplit will stop running comparisons.

### Settings

- Settings files use the extension `.pkl`. Settings files can be saved and opened by using File -> Save Settings As... and File -> Load Settings. A settings file can be loaded upon opening AutoSplit if placed in the same directory as AutoSplit.exe.
- For v1.4 and below, settings work differently. Each time AutoSplit is closed, it saves a the setting file `settings.pkl` to the directory AutoSplit.exe is located in. This settings file must be in the same directory as AutoSplit.exe and is loaded upon opening the program. Settings can be reloaded using the Reload Settings button.
- The settings in the settings file include split image directory, capture region, capture region dimensions, fps limit, threshold and pause time settings, all hotkeys, "Group dummy splits when undoing/skipping" check box, "Loop Split Images" check box, and "Auto Start On Reset" check box.
- If you are upgrading to Windows 11, it's possible that save files may not transfer perfectly. You may need to readjust or reselect your Capture Region, for example.

## Known Limitations
- For many games, it will be difficult to find a split image for the last split of the run.
- The window of the capture region cannot be minimized.

## Known Issues
- Using numpad number keys when numlock is on does not split correctly. Either avoid using numpad or turn numlock off to avoid this issue.
- LiveSplit and wsplit will not split correctly if you are holding shift, ctrl, or alt when a match occurs.
- Numlock on keys are linked to numlock-off keys. For example, if you set your reset hotkey to 2, you can hit arrow down and it will reset and vice versa.

## Resources
- Still need help? [Open an issue](https://github.com/Toufool/Auto-Split/issues)
- Join the [AutoSplit Discord](https://discord.gg/Qcbxv9y)


## Credits
- https://github.com/harupy/ for the snipping tool code that I used to integrate into the autosplitter.
- [amaringos](https://twitter.com/amaringos) for the icon.
- [ZanasoBayncuh](https://twitter.com/ZanasoBayncuh) for motivating me to start this project back up and for all of the time spent testing and suggesting improvements.
- [Avasam](https://twitter.com/Avasam06) for their continued work on making an incredible amount of improvements and changes to AutoSplit while I have not had the time/motivation to do so.
- Created by [Toufool](https://twitter.com/Toufool) and [Faschz](https://twitter.com/faschz).

## Donate
If you enjoy using the program, please consider donating. Thank you!  

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=BYRHQG69YRHBA&item_name=AutoSplit+development&currency_code=USD&source=url)
