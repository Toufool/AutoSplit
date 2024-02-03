from _typeshed import Incomplete
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
    type: int = 2,
    n: Incomplete | None = None,
    axis: int = -1,
    norm: Incomplete | None = None,
    overwrite_x: bool = False,
    workers: Incomplete | None = None,
    orthogonalize: Incomplete | None = None,
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
