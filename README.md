<!-- markdownlint-disable-next-line MD033 -->

# <img src="res/icon.ico" alt="LiveSplit" height="42" width="42" align="top"/> AutoSplit [![CodeQL](/../../actions/workflows/codeql-analysis.yml/badge.svg)](/../../actions/workflows/codeql-analysis.yml) [![Lint and build](/../../actions/workflows/lint-and-build.yml/badge.svg)](/../../actions/workflows/lint-and-build.yml)

[![SemVer](https://badgen.net/badge/_/SemVer%20compliant/grey?label)](https://semver.org/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://docs.astral.sh/ruff/linter/)
[![Ruff format](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/format.json)](https://docs.astral.sh/ruff/formatter/)
[![Checked with pyright](https://microsoft.github.io/pyright/img/pyright_badge.svg)](https://microsoft.github.io/pyright/)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)

Easy to use image comparison based auto splitter for speedrunning on console or PC.

This program can be used to automatically start, split, and reset your preferred speedrun timer by comparing images to a capture region. This allows you to focus more on your speedrun and less on managing your timer. It also improves the accuracy of your splits. It can be used in tandem with any speedrun timer that accepts hotkeys (LiveSplit, WSplit, etc.), and can be integrated with LiveSplit.

<!-- markdownlint-disable-next-line MD033 -->
<p align="center"><img src="./docs/2.2.2.gif" alt="Example" /></p>

## Tutorial

To understand how to use AutoSplit and how it works in-depth, please read the [tutorial](/docs/tutorial.md).

## Download and open

- Download the [latest version](/../../releases/latest)
- You can also check out the [latest dev builds](/../../actions/workflows/lint-and-build.yml?query=event%3Apush+is%3Asuccess) (requires a GitHub account)\
  (If you don't have a GitHub account, you can try [nightly.link](https://nightly.link/Toufool/AutoSplit/workflows/lint-and-build/main))
- Linux users must ensure they are in the `tty` and `input` groups and have write access to `/dev/uinput`. You can run the following commands to do so:

  <!-- https://github.com/boppreh/keyboard/issues/312#issuecomment-1189734564 -->
  <!-- Keep in sync with scripts/install.ps1 and src/error_messages.py -->
  ```shell
  sudo usermod -a -G tty,input $USER
  sudo touch /dev/uinput
  sudo chmod +0666 /dev/uinput
  echo 'KERNEL=="uinput", TAG+="uaccess"' | sudo tee /etc/udev/rules.d/50-uinput.rules
  echo 'SUBSYSTEM=="input", MODE="0666" GROUP="plugdev"' | sudo tee /etc/udev/rules.d/12-input.rules
  echo 'SUBSYSTEM=="misc", MODE="0666" GROUP="plugdev"' | sudo tee -a /etc/udev/rules.d/12-input.rules
  echo 'SUBSYSTEM=="tty", MODE="0666" GROUP="plugdev"' | sudo tee -a /etc/udev/rules.d/12-input.rules
  loginctl terminate-user $USER
  ```

  <!-- Keep in sync with src/error_messages.py -->
  All screen capture method are incompatible with Wayland. Follow [this guide](https://linuxconfig.org/how-to-enable-disable-wayland-on-ubuntu-22-04-desktop) to disable it.

### Compatibility

- Windows 10 and 11.
- Linux (still in early development)
  - Should work on Ubuntu 22.04+
  - Wayland is not currently supported
  - WSL2/WSLg requires an additional Desktop Environment, external X11 server, and/or systemd
- x64 and ARM64 architectures \* (see [Known Limitations](#known-limitations) for ARM64)
- If you'd like to run the project directly in Python from the source code, refer to the [build instructions](/docs/build%20instructions.md).

## Timer Integration

### Timer Global Hotkeys

Out of the box, AutoSplit works by listening for keyboard events and sending virtual keystrokes. This makes AutoSplit compatible with any timer by configuring your hotkeys to be the same. See the [Timer Global Hotkeys Tutorial](/docs/tutorial.md#timer-global-hotkeys).

### LiveSplit Integration

The AutoSplit LiveSplit Component will directly connect AutoSplit with LiveSplit. LiveSplit integration is only supported in AutoSplit v1.6.0 or higher. This integration will allow you to:

- Use hotkeys directly from LiveSplit to control AutoSplit and LiveSplit together
- Load AutoSplit and any AutoSplit profile automatically when opening a LiveSplit layout.

See the [installation instructions](https://github.com/Toufool/LiveSplit.AutoSplitIntegration#installation).

## Known Limitations

- For many games, it will be difficult to find a split image for the last split of the run.
- The window of the capture region cannot be minimized.
- Linux support is incomplete and we're [looking for contributors](../../issues?q=is%3Aissue+is%3Aopen+label%3A"help+wanted"+label%3ALinux+).
  - Incompatible with LiveSplitOne on Linux (see <https://github.com/LiveSplit/LiveSplitOne/issues/1025>)
- Antivirus false positives. Please read <https://github.com/pyinstaller/pyinstaller/blob/develop/.github/ISSUE_TEMPLATE/antivirus.md>
- The Perceptual Hash Comparison Method similarity may differ by 3.125% on ARM64. (this will be solved eventually, we have to use a fallback method for now)
- Native ARM64 builds go completely untested. There may be unforseen issues.

## Resources

Still need help?

<!-- open issues sorted by reactions -->

- [Check if your issue already exists](../../issues?q=is%3Aissue+is%3Aopen+sort%3Areactions-%2B1-desc)
  - If it does, upvote it 👍
  - If it doesn't, create a new one
- Join the [AutoSplit Discord\
  ![AutoSplit Discord](https://badgen.net/discord/members/Qcbxv9y)](https://discord.gg/Qcbxv9y)

## Contributing

See [CONTRIBUTING.md](/docs/CONTRIBUTING.md) for our contributing standards.\
Refer to the [build instructions](/docs/build%20instructions.md) if you're interested in building the application yourself or running it in Python.

Not a developer? You can still help through the following methods:

- Donating (see link below)
- [Upvoting 👍 feature requests](../../issues?q=is%3Aissue+is%3Aopen+sort%3Areactions-%2B1-desc+label%3Aenhancement) you are interested in <!-- open enhancements sorted by reactions -->
- Sharing AutoSplit with other speedrunners
- Starring the repository <img style="vertical-align: sub" src="./docs/repo_star.png" alt="Example" />
- Upvoting 👍 the following upstream issues in libraries and tools we use:
  - <https://bugreports.qt.io/browse/QTBUG-114436>
  - <https://bugreports.qt.io/browse/QTBUG-114635>
  - <https://bugreports.qt.io/browse/PYSIDE-2541>
  - <https://bugreports.qt.io/browse/PYSIDE-2542>
  - <https://github.com/pyinstaller/pyinstaller/issues/9012>
  - <https://github.com/opencv/opencv/issues?q=is%3Aissue+is%3Aopen+involves%3AAvasam+sort%3Areactions-%2B1-asc+>
  - <https://github.com/mypyc/mypyc/issues?q=sort%3Areactions-%2B1%20is%3Aissue%20is%3Aopen%20%20involves%3AAvasam%20>
  - <https://github.com/uiri/toml/issues/270>
  - <https://github.com/microsoft/vscode/issues/40239>
  - <https://github.com/microsoft/vscode/issues/168411>
  - <https://github.com/ronaldoussoren/altgraph/pull/25>
  - <https://github.com/python/mypy/issues/6700>
  - <https://github.com/python/mypy/issues/15146>
  - <https://github.com/python/mypy/issues/4409>
  - <https://github.com/python/mypy/issues/10149>
  - <https://github.com/boppreh/keyboard/issues/171>
  - <https://github.com/boppreh/keyboard/issues/516>
  - <https://github.com/boppreh/keyboard/issues/216>
  - <https://github.com/boppreh/keyboard/issues/161>
  - <https://github.com/asweigart/pyautogui/issues/663>
  - <https://github.com/asweigart/pyautogui/pull/911>
  - <https://github.com/astral-sh/ruff/issues?q=is%3Aissue+is%3Aopen+involves%3AAvasam+sort%3Areactions-%2B1-asc+>

## Credits

- Created by [Toufool](https://twitter.com/Toufool) and [Faschz](https://twitter.com/faschz).
- [Harutaka Kawamura](https://github.com/harupy/) for the snipping tool code that I used to integrate into the autosplitter.
- [amaringos](https://twitter.com/amaringos) for the icon.
- [Zana_G](https://www.twitch.tv/zana_g) for motivating me to start this project back up and for all of the time spent testing and suggesting improvements.
- [Avasam](https://twitter.com/Avasam06) for their continued work on making an incredible amount of improvements and changes to AutoSplit while I have not had the time/motivation to do so.
- [KaDiWa](https://github.com/KaDiWa4) for the LiveSplit integration.
- [Tyron18](https://twitter.com/Tyron18_) for assisting with Windows 11 testing.

## Donate

If you enjoy using the program, please consider donating. Thank you!

[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=BYRHQG69YRHBA&item_name=AutoSplit+development&currency_code=USD&source=url)
