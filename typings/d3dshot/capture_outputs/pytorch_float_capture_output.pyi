import torch
from _typeshed import Incomplete
from d3dshot.capture_output import CaptureOutput as CaptureOutput
from PIL.Image import Image
from typing_extensions import TypeAlias

Pointer: TypeAlias = Incomplete


class PytorchFloatCaptureOutput(CaptureOutput):
    def __init__(self) -> None: ...

    def process(
        self, pointer: Pointer, size: int, width: int, height: int, region: tuple[int, int, int, int], rotation: int
    ) -> torch.Tensor: ...
    def to_pil(self, frame: torch.Tensor) -> Image: ...
    def stack(self, frames: list[torch.Tensor], stack_dimension: int) -> torch.Tensor: ...
