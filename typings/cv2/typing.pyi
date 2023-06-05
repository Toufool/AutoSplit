from collections.abc import Sequence

import numpy as np
from cv2.mat_wrapper import MatLike as WrappedMat
from typing_extensions import TypeAlias

_NDArray: TypeAlias = np.ndarray[float, np.dtype[np.generic]]
MatLike: TypeAlias = WrappedMat | _NDArray

# Convertable to boolean
Boolean: TypeAlias = bool | int | None
# "a scalar"
NumericScalar: TypeAlias = float | bool | None
# cv::Scalar
Scalar: TypeAlias = MatLike | NumericScalar | Sequence[NumericScalar]
# cv::TermCriteria
TermCriteria: TypeAlias = tuple[int, int, float] | Sequence[float]
# cv::Point<int>
Point: TypeAlias = tuple[int, int] | Sequence[int]
# cv::Size<int>
Size: TypeAlias = tuple[int, int] | Sequence[int]
# cv::Range<int>
Range: TypeAlias = tuple[int, int] | Sequence[int]
# cv::Point<float>
Point2f: TypeAlias = tuple[float, float] | Sequence[float]
# cv::Size<float>
SizeFloat: TypeAlias = tuple[float, float] | Sequence[float]
# cv::Rect<int>
Rect: TypeAlias = tuple[int, int, int, int] | Sequence[int]
# cv::Rect<float>
RectFloat: TypeAlias = tuple[int, int, int, int] | Sequence[int]
# cv::RotatedRect
RotatedRect: TypeAlias = tuple[Point2f, SizeFloat, float] | Sequence[Point2f | SizeFloat | float]
RotatedRectResult: TypeAlias = tuple[tuple[float, float], tuple[float, float], float]
