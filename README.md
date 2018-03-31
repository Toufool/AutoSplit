# autosplitter
This program is used together with a speedrun timer (livesplit, wsplit, etc) that uses image analysis to compare images (chosen by the user) to the users live game feed and splits when there is a match. It was created using Python 2.7

# HOW IT WORKS:

Autosplitter takes a folder of images and looks at the first image in the folder (alphabetically) and begins to compare it to your game feed. Once that image meets the "Match % Threshold" compared to your game feed, it presses your split hot key and moves on to the next image in the folder and repeats the procedure until all images have been matched and split.

# TUTORIAL:

## SPLIT IMAGE FOLDER:
- All split images currently must be .jpg files.
- They can be any size.
- Name split images alphabetically in the order you want them to split - an easy way to do this is name the file "a_splitname.jpg, b_splitname.jpg, etc.

A good split image is:
- One that is still or mostly still for a few seconds during gameplay
- One that is unique and does not repeat during the run
    - If it does repeat and you have the same two split images in a row, make sure your "pause" option is long enough so that the program     doesn't split twice, and make sure the image doesn't appear in your game feed again until you want the program to split.
- One that is NOT completely black or completely white - these are common loading screens that could cause false positive matches/splits. However if there is no black or white screens between splits, this is okay to use.

## GAME SCREEN REGION
- Click "Set Top Left", hover your mouse over the top left corner of your game screen and wait a few seconds until the coordinates change in the program
- Click "Set Bottom Right", hover your mouse over the bottom corner of your game screen and wait a few secounds until the coordinates change in the program
- These coordinates do not have to be exact, but try to get them as accurate as you can
- Once both coordinates are set, make sure to not move your game feed (OBS, Xsplit, or any other source that you are using). The coordinates do not follow your game feed - they are viewing your desktop.
Note: Making the game screen region smaller will increase performance. See "Check FPS" in Options below.

## TIMER HOTKEYS
- Click "Set Hotkey" on each option and make sure that they match up to what your hotkeys are in your preferred speedrun timer.

## OPTIONS
### Pause After Split:
- After a match occurs and the program splits, this is the amount of time the program will pause and stop comparing images before it goes to the next split.  If all of your images are unique, there is no need to change this option. 
- If your split image folder has 2 or more split images in a row that are the same (for example, [this image](https://i.imgur.com/lmuSZoP.jpg) that appears in Super Mario Odyssey each time you finish a world) make sure that you pause for enough time so that the program does not split twice.

### Check FPS
- Clicking this button will tell you how many times per second your gamefeed is being compared to the split image. 
- The higher the number, the more accurate the split will be. It is good to keep this number above 30. 
- To increase your FPS, make your Game Screen Region smaller.

### % Match Threshold
- Once the program matches your game screen region with a split image with a number higher than this %, the program will split.
- If the program is not splitting, trying lowering this number
- If the program is splitting too early or not when you want it to, try raising this number. 
- 90% is generally a good starting point, and is the default option. 
- The "test" option will make it so that your program will never split. Good to use for testing split images.
- Check the "Show Live % Match" option to view your game screen region % match to the current split image (shown in the bottom left of the program) in real time

### Start Auto Splitter
- Starts the auto splitter from your first split in your split image folder. The current split image is shown on the bottom left.
- Use the Reset, Undo Split, and Skip Split hotkeys when needed
