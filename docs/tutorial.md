# TUTORIAL

## OPTIONS

#### Split Image Folder

- Supported image file types: PNG, JPEG, bitmaps, WebP, and [more](https://docs.opencv.org/4.8.0/d4/da8/group__imgcodecs.html#imread).
- Images can be any size and ratio.
- Images are matched in alphanumerical order.
  - Note that this can lead to discrepancies between the order of file as seen in your file browser and the order of Split Images in AutoSplit.
  - Windows Explorer displays files in [Natural sort order](https://en.wikipedia.org/wiki/Natural_sort_order).
  - On UNIX-based systems, it depends on your file browser.
- Recommended filenaming convention: `001_SplitName.png, 002_SplitName.png, 003_SplitName.png`...
- Custom split image settings are handled in the filename. See how [here](#custom-split-image-settings).
- To create split images, it is recommended to use AutoSplit's Take Screenshot button for accuracy. However, images can be created using any method including Print Screen and [Snipping Tool](https://support.microsoft.com/en-us/help/4027213/windows-10-open-snipping-tool-and-take-a-screenshot).

#### Capture Region

- This is the region that your split images are compared to. Usually, this is going to be the full game screen.
- Click "Select Region".
- Click and drag to form a rectangle over the region you want to capture.
- Adjust the x, y, width, and height of the capture region manually to make adjustments as needed.
- If you want to align your capture region by using a reference image, click "Align Region".
- You can freely move the window that the program is capturing, but resizing the window will cause the capture region to change.
- Once you are happy with your capture region, you may unselect Live Capture Region to decrease CPU usage if you wish.
- You can save a screenshot of the capture region to your split image folder using the Take Screenshot button.

#### Avg. FPS

- Calculates the average comparison rate of the capture region to split images. This value will likely be much higher than needed, so it is highly recommended to limit your FPS depending on the frame rate of the game you are capturing.

### Settings

#### Comparison Method

- There are three comparison methods to choose from: L2 Norm, Histograms, and Perceptual Hash (aka pHash).
  - L2 Norm: This method should be fine to use for most cases. It finds the difference between each pixel, squares it, sums it over the entire image and takes the square root. This is very fast but is a problem if your image is high frequency. Any translational movement or rotation can cause similarity to be very different.
  - Histograms: An explanation on Histograms comparison can be found [here](https://mpatacchiola.github.io/blog/2016/11/12/the-simplest-classifier-histogram-intersection.html). This is a great method to use if you are using several masked images.
    > This algorithm is particular reliable when the colour is a strong predictor of the object identity. The histogram intersection [...] is robust to occluding objects in the foreground.
  - Perceptual Hash: An explanation on pHash comparison can be found [here](http://www.hackerfactor.com/blog/index.php?/archives/432-Looks-Like-It.html). It is highly recommended to NOT use pHash if you use masked images, or it'll be very inaccurate.

#### Capture Method

<!-- Keep all descriptions in sync with in-code descriptions in src/capture_method/*CaptureMethod.py-->

##### Windows

- **Windows Graphics Capture** (fast, most compatible, capped at 60fps)\
  Only available in Windows 10.0.17134 and up.\
  Allows recording UWP apps, Hardware Accelerated and Exclusive Fullscreen windows.\
  Adds a yellow border on Windows 10 (not on Windows 11).
  Caps at around 60 FPS.
- **BitBlt** (fastest, least compatible)\
  The best option when compatible. But it cannot properly record OpenGL, Hardware Accelerated or Exclusive Fullscreen windows.\
  The smaller the selected region, the more efficient it is.
- **Direct3D Desktop Duplication** (slower, bound to display)\
  Duplicates the desktop using Direct3D.\
  It can record OpenGL and Hardware Accelerated windows.\
  Up to 15x slower than BitBlt for tiny regions. Not affected by window size.
  Limited by the target window and monitor's refresh rate.
  Overlapping windows will show up and can't record across displays.\
  This option may not be available for hybrid GPU laptops, see [D3DDD-Note-Laptops.md](/docs/D3DDD-Note-Laptops.md) for a solution.
- **Force Full Content Rendering** (very slow, can affect rendering)\
  Uses BitBlt behind the scene, but passes a special flag to PrintWindow to force rendering the entire desktop.\
  About 10-15x slower than BitBlt based on original window size and can mess up some applications' rendering pipelines.

##### Linux

- **X11 XCB** (slower, requires XCB)\
  Uses the XCB library to take screenshots of the X11 server.
- **Scrot** (fast, may leave files in `/tmp`)\
  Uses Scrot (SCReenshOT) to take screenshots.\
  Leaves behind a screenshot file in `/tmp` if interrupted.
  <!-- Keep in sync with src/menu_bar.py -->
  "scrot" must be installed: `sudo apt-get install scrot`

##### All platforms

- **Video Capture Device**\
  Uses a Video Capture Device, like a webcam, virtual cam, or capture card.\
  You can select one from the `Capture Device` dropdown below.\
  See [this guide](https://obsproject.com/kb/virtual-camera-guide) on using the OBS Virtual Camera.

#### Capture Device

Select the Video Capture Device that you wanna use if selecting the `Video Capture Device` Capture Method.

<!-- Will show `[occupied]` if a device is detected but can't be started. (feature currently disabled because poking at devices to turn turn them off freezes some like the GV-USB2)-->

#### Show Live Similarity

- Displays the live similarity between the capture region and the current split image. This number is between 0 and 1, with 1 being a perfect match.

#### Show Highest Similarity

- Shows the highest similarity between the capture region and current split image.

#### Current Similarity Threshold

- When the live similarity goes above this value, the program hits your split hotkey and moves to the next split image.

#### Default Similarity Threshold

- This value will be set as the threshold for an image if there is no custom threshold set for that image.

#### Default Delay Time

- Time in milliseconds that the program waits before hitting the split hotkey for that specific split if there is no custom Delay Time set for that image.

#### Default Pause Time

- Time in seconds that the program stops comparison after a split if there is no custom Pause Time set for that image. Useful for if you have two of the same split images in a row and want to avoid double-splitting. Also useful for reducing CPU usage.

#### Dummy splits when undoing / skipping

AutoSplit will group dummy splits together with a real split when undoing/skipping. This basically allows you to tie one or more dummy splits to a real split to keep it as in sync as possible with the real splits in LiveSplit/wsplit. If they are out of sync, you can always use "Previous Image" and "Next Image".

Examples:
Given these splits: 1 dummy, 2 normal, 3 dummy, 4 dummy, 5 normal, 6 normal.

In this situation you would have only 3 splits in LiveSplit/wsplit (even though there are 6 split images, only 3 are "real" splits). This basically results in 3 groups of splits: 1st split is images 1 and 2. 2nd split is images 3, 4 and 5. 3rd split is image 6.

- If you are in the 1st or 2nd image and press the skip key, it will end up on the 3rd image
- If you are in the 3rd, 4th or 5th image and press the undo key, it will end up on the 2nd image
- If you are in the 3rd, 4th or 5th image and press the skip key, it will end up on the 6th image
- If you are in the 6th image and press the undo key, it will end up on the 5th image

#### Loop last Split Image to first Split Image

If this option is enabled, when the last split meets the threshold and splits, AutoSplit will loop back to the first split image and continue comparisons.
If this option is disabled, when the last split meets the threshold and splits, AutoSplit will stop running comparisons.
This option does not loop single, specific images. See the Custom Split Image Settings section above for this feature.

#### Start also Resets

If this option is enabled, a "Start" command (ie: from the Start Image) will also send the "Reset" command. This is useful if you want to automatically restart your timer using the Start Image. Since AutoSplit won't be running and won't be checking for the Reset Image.

Having the reset image check be active at all time would be a better, more organic solution in the future. But that is dependent on migrating to an observer pattern (<https://github.com/Toufool/AutoSplit/issues/219>) and being able to reload all images.

#### Enable auto Reset Image

This option is mainly meant to be toggled with the `Toggle auto Reset Image` hotkey. You can enable it to temporarily disable the Reset Image if you make a mistake in your run that would cause the Reset Image to trigger. Like exiting back to the game's menu (aka Save&Quit).

### Custom Split Image Settings

- Each split image can have different thresholds, pause times, delay split times, loop amounts, and can be flagged.
- These settings are handled in the image's filename.
- **Custom thresholds** are place between parenthesis `()` in the filename. This value will override the default threshold.
- **Custom pause times** are placed between square brackets `[]` in the filename. This value will override the default pause time.
- **Custom delay times** are placed between hash signs `##` in the filename. Note that these are in milliseconds. For example, a 10 second split delay would be `#10000#`. You cannot skip or undo splits during split delays.
- A different **comparison method** can be specified with their 0-base index between carets `^^`:
  - `^0^`: L2 Norm
  - `^1^`: Histogram
  - `^2^`: Perceptual Hash
- **Image loop** amounts are placed between at symbols `@@` in the filename. For example, a specific image that you want to split 5 times in a row would be `@5@`. The current loop # is conveniently located beneath the current split image.
- **Flags** are placed between curly brackets `{}` in the filename. Multiple flags are placed in the same set of curly brackets. Current available flags:
  - `{d}` **dummy split image**. When matched, it moves to the next image without hitting your split hotkey.
  - `{b}` split when **similarity goes below** the threshold rather than above. When a split image filename has this flag, the split image similarity will go above the threshold, do nothing, and then split the next time the similarity goes below the threshold.
  - `{p}` **pause flag**. When a split image filename has this flag, it will hit your pause hotkey rather than your split hokey.
- Filename examples:
  - `001_SplitName_(0.9)_[10].png` is a split image with a threshold of 0.9 and a pause time of 10 seconds.
  - `002_SplitName_(0.9)_[10]_{d}.png` is the second split image with a threshold of 0.9, pause time of 10, and is a dummy split.
  - `003_SplitName_(0.85)_[20]_#3500#.png` is the third split image with a threshold of 0.85, pause time of 20 and has a delay split time of 3.5 seconds.
  - `004_SplitName_(0.9)_[10]_#3500#_@3@_{b}.png` is the fourth split image with a threshold of 0.9, pause time of 10 seconds, delay split time of 3.5 seconds, will loop 3 times, and will split when similarity is below the threshold rather than above.

## Special images

### How to Create a Masked Image

Masked images are very useful if only a certain part of the capture region is consistent (for example, consistent text on the screen, but the background is always different). Histogram or L2 norm comparison is recommended if you use any masked images. It is highly recommended that you do NOT use pHash comparison if you use any masked images, or it'll be very inaccurate.

The best way to create a masked image is to set your capture region as the entire game screen, take a screenshot, and use a program like [paint.net](https://www.getpaint.net/) to "erase" (make transparent) everything you don't want the program to compare. More on creating images with transparency using paint.net can be found in [this tutorial](https://www.youtube.com/watch?v=v53kkUYFVn8). For visualization, here is what the capture region compared to a masked split image looks like if you would want to split on "Shine Get!" text in Super Mario Sunshine:

![Mask Example](/docs/mask_example_image.png)

### Reset Image

You can have one (and only one) image with the keyword `reset` in its name. AutoSplit will press the reset button when it finds this image. This image will only be used for resets and it will not be tied to any split. You can set a threshold and pause time for it. The pause time is the amount of seconds AutoSplit will wait before checking for the Reset Image once the run starts. For example: `Reset_(0.95)_[10].png`.

### Start Image

The Start Image is similar to the Reset Image. You can only have one Start Image with the keyword `start_auto_splitter`.You can reload the image using the "`Reload Start Image`" button. The pause time is the amount of seconds AutoSplit will wait before starting comparisons of the first split image. Delay times will be used to delay starting your timer after the threshold is met.

### Text Recognition / Optical Character Recognition (OCR) ⚠️EXPERIMENTAL⚠️

You can use text recognition as an alternative comparison method.

#### Tesseract install

First you need to install tesseract and include it in your system or user environment variables.

- See <https://tesseract-ocr.github.io/tessdoc/Installation.html> for installation instruction on all platforms.
- For Windows:
  1. You can go directly to <https://github.com/UB-Mannheim/tesseract/wiki> to find the installer.
  2. If you change the "Destination Folder" during install, then you'll also need to add it to your `PATH` environment variable.

#### Usage

To use this feature you need to place a text file (`.txt`) in your splits folder instead of an image file.

An example file name and content could look like this:

Filename: `001_start_auto_splitter.txt`

Content:

```toml
texts = ["complete any 2 encounters"]
left = 275
right = 540
top = 70
bottom = 95
methods = [0]
fps_limit = 1
```

The `texts` field is an array and can take more than one text to look for:

```toml
texts = ["look for me", "or this text"]
```

Note: for now we only use lowercase letters in the comparison. All uppercase letters are converted to lowercase before the comparison.

The rectangle coordinates where the text you are looking for is expected to appear in the image are configured as follows:

```toml
left = 275
right = 540
top = 70
bottom = 95
```

If you're used to working in corner coordinates, you can think of `top_left = [left, top]` and `bottom_right = [right, bottom]`.

Currently there are two comparison methods:

- `0` - uses the Levenshtein distance (the default)
- `1` - checks if the OCR text contains the searched text (results in matches of either `0.0` or `1.0`)

If you only want a perfect full match, use "Levenshtein" with a threshold of `(1.0)` on your file name.

You can also chain multiple comparison methods using the array notation:

```toml
methods = [1, 0]
```

The methods are then checked in the order you defined and the best match upon them wins.

Note: This method can cause high CPU usage at the standard comparison FPS. You should therefor limit the comparison FPS when you use this method to 1 or 2 FPS using the `fps_limit` option.\
The size of the selected rectangle can also impact the CPU load (bigger = more CPU load).

### Profiles

<!-- TODO: Profiles are saved under `%appdata%\AutoSplit\profiles` and -->

- Profiles use the extension `.toml`. Profiles can be saved and loaded by using `File -> Save Profile As...` and `File -> Load Profile`.
- The profile contains all of your settings, including information about the capture region.
- You can save multiple profiles, which is useful if you speedrun multiple games.
- If you change your display setup (like using a new monitor, or upgrading to Windows 11), you may need to readjust or reselect your Capture Region.

## Timer Integration Tutorial

### Timer Global Hotkeys

- Click "Set Hotkey" on each hotkey to set the hotkeys to AutoSplit. The Start / Split hotkey and Pause hotkey must be the same as the one used in your preferred timer program in order for the splitting/pausing to work properly.
- Make sure that Global Hotkeys are enabled in your speedrun timer.
- All of these actions can also be handled by their corresponding buttons.
- Note that pressing your Pause Hotkey does not serve any function in AutoSplit itself and is strictly used for the Pause flag.

#### LiveSplit Integration

See the [usage instructions](https://github.com/Toufool/LiveSplit.AutoSplitIntegration#openingclosing-autosplit).
