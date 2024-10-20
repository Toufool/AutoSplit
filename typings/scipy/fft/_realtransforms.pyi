from typing import Literal

from numpy import float64, generic
from numpy.typing import NDArray

__all__ = ["dct", "dctn", "dst", "dstn", "idct", "idctn", "idst", "idstn"]

def dctn(
    x,
    type=2,
    s=None,
    axes=None,
    norm=None,
    overwrite_x=False,
    workers=None,
    *,
    orthogonalize=None,
): ...
def idctn(
    x,
    type=2,
    s=None,
    axes=None,
    norm=None,
    overwrite_x=False,
    workers=None,
    orthogonalize=None,
): ...
def dstn(
    x,
    type=2,
    s=None,
    axes=None,
    norm=None,
    overwrite_x=False,
    workers=None,
    orthogonalize=None,
): ...
def idstn(
    x,
    type=2,
    s=None,
    axes=None,
    norm=None,
    overwrite_x=False,
    workers=None,
    orthogonalize=None,
): ...
def dct(
    x: NDArray[generic],
    type: Literal[1, 2, 3, 4] = 2,
    n: int | None = None,
    axis: int = -1,
    norm: Literal["backward", "ortho", "forward"] | None = None,
    overwrite_x: bool = False,
    workers: int | None = None,
    orthogonalize: bool | None = None,
) -> NDArray[float64]: ...
def idct(
    x,
    type=2,
    n=None,
    axis=-1,
    norm=None,
    overwrite_x=False,
    workers=None,
    orthogonalize=None,
): ...
def dst(
    x,
    type=2,
    n=None,
    axis=-1,
    norm=None,
    overwrite_x=False,
    workers=None,
    orthogonalize=None,
): ...
def idst(
    x,
    type=2,
    n=None,
    axis=-1,
    norm=None,
    overwrite_x=False,
    workers=None,
    orthogonalize=None,
): ...
