# Install and Build instructions

## Requirements

### Windows

- Microsoft Visual C++ 14.0 or greater may be required to build the executable. Get it with [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/).  

### Linux

- You need to be part of the `input` and `tty` groups, as well as have permissions on a few files and folders.  
  If you are missing from either groups, the install script will take care of it on its first run, but you'll need to restart your session.  

### WSL

If using WSL to test on Windows, you might need to tell uv to point to a different environment than `.venv`. You can point to your system environment by running:

```shell
export UV_PROJECT_ENVIRONMENT=$(python3 -c "import sysconfig; print(sysconfig.get_config_var('prefix'))")
```

Read more: <https://docs.astral.sh/uv/concepts/projects/config/#project-environment-path>

### All platforms

- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- [PowerShell](https://learn.microsoft.com/en-us/powershell/scripting/install/installing-powershell) is used to run all the scripts.
  - This is needed even for Windows, as the bundled PowerShell 5.1 is too old.
- [VSCode](https://code.visualstudio.com/Download) is not required, but highly recommended.
  - Everything already configured in the workspace, including Run (F5) and Build (Ctrl+Shift+B) commands, default shell, and recommended extensions.
  - [PyCharm](https://www.jetbrains.com/pycharm/) is also a good Python IDE, but nothing is configured. If you are a PyCharm user, feel free to open a PR with all necessary workspace configurations!

## Install and Build steps

- Run `./scripts/install.ps1` to create/update a virtual environment and install all dependencies.
- Run the app directly with `./scripts/start.ps1 [--auto-controlled]`.
  - Or debug by pressing `F5` in VSCode.
  - The `--auto-controlled` flag is passed when AutoSplit is started by LiveSplit.
- Run `./scripts/build.ps1` or press `CTRL+Shift+B` in VSCode to build an executable.
- Optional: Recompile resources after modifications by running `./scripts/compile_resources.ps1`.
  - This should be done automatically by other scripts
