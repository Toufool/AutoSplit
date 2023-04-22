import numpy
from typing_extensions import TypeAlias

_Unused: TypeAlias = object

__all__: list[str] = []


_NDArray = numpy.ndarray[float, numpy.dtype[numpy.generic]]

# TODO: Make Mat generic with int or float


class Mat(_NDArray):
    wrap_channels: bool | None

    def __new__(cls, arr: _NDArray, wrap_channels: bool = ..., **kwargs: _Unused) -> _NDArray: ...
    def __init__(self, arr: _NDArray, wrap_channels: bool = ...) -> None: ...
    def __array_finalize__(self, obj: _NDArray | None) -> None: ...
