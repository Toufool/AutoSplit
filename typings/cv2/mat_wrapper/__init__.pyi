import numpy as np
from _typeshed import Unused
from typing_extensions import TypeAlias

__all__: list[str] = []
_NDArray: TypeAlias = np.ndarray[float, np.dtype[np.generic]]


class Mat(_NDArray):
    wrap_channels: bool | None

    def __new__(cls, arr: _NDArray, wrap_channels: bool = ..., **kwargs: Unused) -> _NDArray: ...
    def __init__(self, arr: _NDArray, wrap_channels: bool = ...) -> None: ...
    def __array_finalize__(self, obj: _NDArray | None) -> None: ...
