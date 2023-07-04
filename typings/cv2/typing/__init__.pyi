import typing

import cv2
import cv2.dnn
import cv2.gapi.wip.draw
import cv2.mat_wrapper
import numpy

IntPointer = int
"""Represents an arbitrary pointer"""
MatLike = cv2.mat_wrapper.Mat | numpy.ndarray[typing.Any, numpy.dtype[numpy.generic]]
MatShape = typing.Sequence[int]
Size = typing.Sequence[int]
"""Required length is 2"""
Size2f = typing.Sequence[float]
"""Required length is 2"""
Scalar = typing.Sequence[float]
"""Required length is at most 4"""
Point = typing.Sequence[int]
"""Required length is 2"""
Point2i = Point
Point2f = typing.Sequence[float]
"""Required length is 2"""
Point2d = typing.Sequence[float]
"""Required length is 2"""
Point3i = typing.Sequence[int]
"""Required length is 3"""
Point3f = typing.Sequence[float]
"""Required length is 3"""
Point3d = typing.Sequence[float]
"""Required length is 3"""
Range = typing.Sequence[int]
"""Required length is 2"""
Rect = typing.Sequence[int]
"""Required length is 4"""
Rect2i = typing.Sequence[int]
"""Required length is 4"""
Rect2d = typing.Sequence[float]
"""Required length is 4"""
Moments = dict[str, float]
RotatedRect = tuple[Point2f, Size, float]
"""Any type providing sequence protocol is supported"""
TermCriteria = tuple[cv2.TermCriteria_Type, int, float]
"""Any type providing sequence protocol is supported"""
Vec2i = typing.Sequence[int]
"""Required length is 2"""
Vec2f = typing.Sequence[float]
"""Required length is 2"""
Vec2d = typing.Sequence[float]
"""Required length is 2"""
Vec3i = typing.Sequence[int]
"""Required length is 3"""
Vec3f = typing.Sequence[float]
"""Required length is 3"""
Vec3d = typing.Sequence[float]
"""Required length is 3"""
Vec4i = typing.Sequence[int]
"""Required length is 4"""
Vec4f = typing.Sequence[float]
"""Required length is 4"""
Vec4d = typing.Sequence[float]
"""Required length is 4"""
Vec6f = typing.Sequence[float]
"""Required length is 6"""
FeatureDetector = cv2.Feature2D
DescriptorExtractor = cv2.Feature2D
FeatureExtractor = cv2.Feature2D
GProtoArg = Scalar | cv2.GMat | cv2.GOpaqueT | cv2.GArrayT
GProtoInputArgs = typing.Sequence[GProtoArg]
GProtoOutputArgs = typing.Sequence[GProtoArg]
GRunArg = MatLike | Scalar | cv2.GOpaqueT | cv2.GArrayT | typing.Sequence[typing.Any] | None
GOptRunArg = GRunArg | None
GMetaArg = cv2.GMat | Scalar | cv2.GOpaqueT | cv2.GArrayT
Prim = (
    cv2.gapi.wip.draw.Text
    | cv2.gapi.wip.draw.Circle
    | cv2.gapi.wip.draw.Image
    | cv2.gapi.wip.draw.Line
    | cv2.gapi.wip.draw.Rect
    | cv2.gapi.wip.draw.Mosaic
    | cv2.gapi.wip.draw.Poly
)
Matx33f = numpy.ndarray[typing.Any, numpy.dtype[numpy.float32]]
"""Shape: (3, 3)"""
Matx33d = numpy.ndarray[typing.Any, numpy.dtype[numpy.float64]]
"""Shape: (3, 3)"""
Matx44f = numpy.ndarray[typing.Any, numpy.dtype[numpy.float32]]
"""Shape: (4, 4)"""
Matx44d = numpy.ndarray[typing.Any, numpy.dtype[numpy.float64]]
"""Shape: (4, 4)"""
GTypeInfo = cv2.GMat | Scalar | cv2.GOpaqueT | cv2.GArrayT
ExtractArgsCallback = typing.Callable[[typing.Sequence[GTypeInfo]], typing.Sequence[GRunArg]]
ExtractMetaCallback = typing.Callable[[typing.Sequence[GTypeInfo]], typing.Sequence[GMetaArg]]
LayerId = cv2.dnn.DictValue
IndexParams = dict[str, bool | int | float | str]
SearchParams = dict[str, bool | int | float | str]
