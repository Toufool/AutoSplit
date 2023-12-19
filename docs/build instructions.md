# Install and Build instructions

## Requirements

### Windows

- Microsoft Visual C++ 14.0 or greater may be required to build the executable. Get it with [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/).  

### All platforms

- [Python](https://www.python.org/downloads/) 3.10+.
- [Node](https://nodejs.org) is optional, but required for complete linting.
  - Alternatively you can install the [pyright python wrapper](https://pypi.org/project/pyright/) which has a bit of an overhead delay.
- [PowerShell](https://learn.microsoft.com/en-us/powershell/scripting/install/installing-powershell) is used to run all the scripts
- [VSCode](https://code.visualstudio.com/Download) is not required, but highly recommended.
  - Everything already configured in the workspace, including Run (F5) and Build (Ctrl+Shift+B) commands, default shell, and recommended extensions.
  - [PyCharm](https://www.jetbrains.com/pycharm/) is also a good Python IDE, but nothing is configured. If you are a PyCharm user, feel free to open a PR with all necessary workspace configurations!

## Install and Build steps

- Create and activate a virtual environment:
  - Windows / PowerShell:
    - `python -m venv .venv`
    - `& ./.venv/Scripts/Activate.ps1`
  - Unix / Bash:
    - `python3 -m venv .venv`
    - `source .venv/bin/activate`
- Run `./scripts/install.ps1` to install all dependencies.
  - If you're having issues with the PySide generated code, you might want to first run `pip uninstall -y shiboken6 PySide6 PySide6-Essentials`
- Run the app directly with `./scripts/start.ps1 [--auto-controlled]`.
  - Or debug by pressing `F5` in VSCode.
  - The `--auto-controlled` flag is passed when AutoSplit is started by LiveSplit.
- Run `./scripts/build.ps1` or press `CTRL+Shift+B` in VSCode to build an executable.
- Optional: Recompile resources after modifications by running `./scripts/compile_resources.ps1`.
  - This should be done automatically by other scripts
