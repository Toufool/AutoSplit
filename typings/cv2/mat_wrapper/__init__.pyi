from _typeshed import Unused
from cv2.typing import _NDArray

__all__: list[str] = []


# TODO: Make MatLike generic with int or float


class MatLike(_NDArray):
    wrap_channels: bool | None

    def __new__(cls, arr: _NDArray, wrap_channels: bool = ..., **kwargs: Unused) -> _NDArray: ...
    def __init__(self, arr: _NDArray, wrap_channels: bool = ...) -> None: ...
    def __array_finalize__(self, obj: _NDArray | None) -> None: ...
