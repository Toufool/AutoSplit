__all__ = [
    "IntPointer",
    "MatLike",
    "MatShape",
    "Size",
    "Size2f",
    "Scalar",
    "Point",
    "Point2i",
    "Point2f",
    "Point2d",
    "Point3i",
    "Point3f",
    "Point3d",
    "Range",
    "Rect",
    "Rect2i",
    "Rect2d",
    "Moments",
    "RotatedRect",
    "TermCriteria",
    "Vec2i",
    "Vec2f",
    "Vec2d",
    "Vec3i",
    "Vec3f",
    "Vec3d",
    "Vec4i",
    "Vec4f",
    "Vec4d",
    "Vec6f",
    "FeatureDetector",
    "DescriptorExtractor",
    "FeatureExtractor",
    "GProtoArg",
    "GProtoInputArgs",
    "GProtoOutputArgs",
    "GRunArg",
    "GOptRunArg",
    "GMetaArg",
    "Prim",
    "Matx33f",
    "Matx33d",
    "Matx44f",
    "Matx44d",
    "GTypeInfo",
    "ExtractArgsCallback",
    "ExtractMetaCallback",
    "LayerId",
    "IndexParams",
    "SearchParams",
    "map_string_and_string",
    "map_string_and_int",
    "map_string_and_vector_size_t",
    "map_string_and_vector_float",
    "map_int_and_double",
]

import typing

import cv2
import cv2.dnn
import cv2.gapi.wip.draw
import cv2.mat_wrapper
import numpy
from typing_extensions import TypeAlias

NumPyArrayGeneric: TypeAlias = numpy.ndarray[typing.Any, numpy.dtype[numpy.generic]]
NumPyArrayFloat32: TypeAlias = numpy.ndarray[typing.Any, numpy.dtype[numpy.float32]]
NumPyArrayFloat64: TypeAlias = numpy.ndarray[typing.Any, numpy.dtype[numpy.float64]]
TermCriteria_Type: TypeAlias = cv2.TermCriteria_Type

IntPointer: TypeAlias = int
"""Represents an arbitrary pointer"""
MatLike: TypeAlias = typing.Union[cv2.mat_wrapper.Mat, NumPyArrayGeneric]
MatShape: TypeAlias = typing.Sequence[int]
Size: TypeAlias = typing.Sequence[int]
"""Required length is 2"""
Size2f: TypeAlias = typing.Sequence[float]
"""Required length is 2"""
Scalar: TypeAlias = typing.Sequence[float]
"""Required length is at most 4"""
Point: TypeAlias = typing.Sequence[int]
"""Required length is 2"""
Point2i: TypeAlias = Point
Point2f: TypeAlias = typing.Sequence[float]
"""Required length is 2"""
Point2d: TypeAlias = typing.Sequence[float]
"""Required length is 2"""
Point3i: TypeAlias = typing.Sequence[int]
"""Required length is 3"""
Point3f: TypeAlias = typing.Sequence[float]
"""Required length is 3"""
Point3d: TypeAlias = typing.Sequence[float]
"""Required length is 3"""
Range: TypeAlias = typing.Sequence[int]
"""Required length is 2"""
Rect: TypeAlias = typing.Sequence[int]
"""Required length is 4"""
Rect2i: TypeAlias = typing.Sequence[int]
"""Required length is 4"""
Rect2d: TypeAlias = typing.Sequence[float]
"""Required length is 4"""
Moments: TypeAlias = dict[str, float]
RotatedRect: TypeAlias = tuple[Point2f, Size, float]
"""Any type providing sequence protocol is supported"""
TermCriteria: TypeAlias = tuple[TermCriteria_Type, int, float]
"""Any type providing sequence protocol is supported"""
Vec2i: TypeAlias = typing.Sequence[int]
"""Required length is 2"""
Vec2f: TypeAlias = typing.Sequence[float]
"""Required length is 2"""
Vec2d: TypeAlias = typing.Sequence[float]
"""Required length is 2"""
Vec3i: TypeAlias = typing.Sequence[int]
"""Required length is 3"""
Vec3f: TypeAlias = typing.Sequence[float]
"""Required length is 3"""
Vec3d: TypeAlias = typing.Sequence[float]
"""Required length is 3"""
Vec4i: TypeAlias = typing.Sequence[int]
"""Required length is 4"""
Vec4f: TypeAlias = typing.Sequence[float]
"""Required length is 4"""
Vec4d: TypeAlias = typing.Sequence[float]
"""Required length is 4"""
Vec6f: TypeAlias = typing.Sequence[float]
"""Required length is 6"""
FeatureDetector: TypeAlias = cv2.Feature2D
DescriptorExtractor: TypeAlias = cv2.Feature2D
FeatureExtractor: TypeAlias = cv2.Feature2D
GProtoArg: TypeAlias = typing.Union[Scalar, cv2.GMat, cv2.GOpaqueT, cv2.GArrayT]
GProtoInputArgs: TypeAlias = typing.Sequence[GProtoArg]
GProtoOutputArgs: TypeAlias = typing.Sequence[GProtoArg]
GRunArg: TypeAlias = typing.Union[MatLike, Scalar, cv2.GOpaqueT, cv2.GArrayT, typing.Sequence[typing.Any], None]
GOptRunArg: TypeAlias = typing.Optional[GRunArg]
GMetaArg: TypeAlias = typing.Union[cv2.GMat, Scalar, cv2.GOpaqueT, cv2.GArrayT]
Prim: TypeAlias = typing.Union[
    cv2.gapi.wip.draw.Text, cv2.gapi.wip.draw.Circle, cv2.gapi.wip.draw.Image,
    cv2.gapi.wip.draw.Line, cv2.gapi.wip.draw.Rect, cv2.gapi.wip.draw.Mosaic, cv2.gapi.wip.draw.Poly,
]
Matx33f: TypeAlias = NumPyArrayFloat32
"""NDArray(shape=(3, 3), dtype=numpy.float32)"""
Matx33d: TypeAlias = NumPyArrayFloat64
"""NDArray(shape=(3, 3), dtype=numpy.float64)"""
Matx44f: TypeAlias = NumPyArrayFloat32
"""NDArray(shape=(4, 4), dtype=numpy.float32)"""
Matx44d: TypeAlias = NumPyArrayFloat64
"""NDArray(shape=(4, 4), dtype=numpy.float64)"""
GTypeInfo: TypeAlias = typing.Union[cv2.GMat, Scalar, cv2.GOpaqueT, cv2.GArrayT]
ExtractArgsCallback: TypeAlias = typing.Callable[[typing.Sequence[GTypeInfo]], typing.Sequence[GRunArg]]
ExtractMetaCallback: TypeAlias = typing.Callable[[typing.Sequence[GTypeInfo]], typing.Sequence[GMetaArg]]
LayerId: TypeAlias = cv2.dnn.DictValue
IndexParams: TypeAlias = dict[str, typing.Union[bool, int, float, str]]
SearchParams: TypeAlias = dict[str, typing.Union[bool, int, float, str]]
map_string_and_string: TypeAlias = dict[str, str]
map_string_and_int: TypeAlias = dict[str, int]
map_string_and_vector_size_t: TypeAlias = dict[str, typing.Sequence[int]]
map_string_and_vector_float: TypeAlias = dict[str, typing.Sequence[float]]
map_int_and_double: TypeAlias = dict[int, float]
