from __future__ import annotations

from capture_method.BitBltCaptureMethod import BitBltCaptureMethod


class ForceFullContentRenderingCaptureMethod(BitBltCaptureMethod):
    name = "Force Full Content Rendering"
    short_description = "very slow, can affect rendering"
    description = (
        "\nUses BitBlt behind the scene, but passes a special flag "
        + "\nto PrintWindow to force rendering the entire desktop. "
        + "\nAbout 10-15x slower than BitBlt based on original window size "
        + "\nand can mess up some applications' rendering pipelines. "
    )
    _render_full_content = True
