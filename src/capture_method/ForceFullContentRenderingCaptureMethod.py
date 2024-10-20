import sys

if sys.platform != "win32":
    raise OSError
from capture_method.BitBltCaptureMethod import BitBltCaptureMethod


class ForceFullContentRenderingCaptureMethod(BitBltCaptureMethod):
    name = "Force Full Content Rendering"
    short_description = "very slow, can affect rendering"
    description = """
Uses BitBlt behind the scene, but passes a special flag
to PrintWindow to force rendering the entire desktop.
About 10-15x slower than BitBlt based on original window size
and can mess up some applications' rendering pipelines."""

    _render_full_content = True
