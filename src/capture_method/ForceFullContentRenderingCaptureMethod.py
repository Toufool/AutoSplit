from __future__ import annotations

import sys

if sys.platform != "win32":
    raise OSError

from capture_method.BitBltCaptureMethod import BitBltCaptureMethod


class ForceFullContentRenderingCaptureMethod(BitBltCaptureMethod):
    _render_full_content = True
