from numpy.fft import ifft as ifft
from numpy.random import rand as rand, randn as randn
from scipy import (
    cluster,
    constants,
    datasets,
    fft,
    fftpack,
    integrate,
    interpolate,
    io,
    linalg,
    misc,
    ndimage,
    odr,
    optimize,
    signal,
    sparse,
    spatial,
    special,
    stats,
)
from scipy.__config__ import show as show_config
from scipy._lib._ccallback import LowLevelCallable
from scipy._lib._testutils import PytestTester
from scipy.version import version as __version__

__all__ = [
    "LowLevelCallable",
    "__version__",
    "cluster",
    "constants",
    "datasets",
    "fft",
    "fftpack",
    "integrate",
    "interpolate",
    "io",
    "linalg",
    "misc",
    "ndimage",
    "odr",
    "optimize",
    "show_config",
    "signal",
    "sparse",
    "spatial",
    "special",
    "stats",
    "test",
]

test: PytestTester

def __dir__() -> list[str]: ...
