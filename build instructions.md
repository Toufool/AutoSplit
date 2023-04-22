# Install and Build instructions

## Requirements

### Windows

- Microsoft Visual C++ 14.0 or greater may be required to build the executable. Get it with [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/).  

### All platforms

- [Python](https://www.python.org/downloads/) 3.9+.
- [Node](https://nodejs.org) is optional, but required for complete linting.
  - Alternatively you can install the [pyright python wrapper](https://pypi.org/project/pyright/) which has a bit of an overhead delay.
- [VSCode](https://code.visualstudio.com/Download) is not required, but highly recommended.
  - Everything already configured in the workspace, including Run (F5) and Build (Ctrl+Shift+B) commands, default shell, and recommended extensions.
  - [PyCharm](https://www.jetbrains.com/pycharm/) is also a good Python IDE, but nothing is configured. If you are a PyCharm user, feel free to open a PR with all necessary workspace configurations!

## Install and Build steps

- Read [requirements.txt](/scripts/requirements.txt) for more information on how to install, run and build the python code.
  - Run `./scripts/install.ps1` to install all dependencies.
  - Run the app directly with `./scripts/start.ps1 [--auto-controlled]`.
    - Or debug by pressing `F5` in VSCode
  - Run `./scripts/build.ps1` or press `CTRL+Shift+B` in VSCode to build an executable.
- Recompile resources after modifications by running `./scripts/compile_resources.ps1`.
