"""
Copyright (c) 2020 PyInstaller Development Team.

This file is distributed under the terms of the GNU General Public
License (version 2.0 or later).

The full license is available in LICENSE.GPL.txt, distributed with
this software.

SPDX-License-Identifier: GPL-2.0-or-later

https://github.com/pyinstaller/pyinstaller-hooks-contrib/blob/master/src/_pyinstaller_hooks_contrib/hooks/stdhooks/hook-cv2.py
"""

from PyInstaller.utils.hooks import collect_dynamic_libs, collect_data_files

hiddenimports = ["numpy"]

# Include any DLLs from site-packages/cv2 (opencv_videoio_ffmpeg*.dll can be found there in the PyPI version)
binaries = collect_dynamic_libs("cv2")

# https://github.com/pyinstaller/pyinstaller-hooks-contrib/issues/110
# OpenCV loader from 4.5.4.60 requires extra config files and modules
datas = collect_data_files("cv2", include_py_files=True, includes=["**/*.py"])
