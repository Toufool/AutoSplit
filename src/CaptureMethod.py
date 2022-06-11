import asyncio
from collections import OrderedDict
from dataclasses import dataclass
from enum import Enum, EnumMeta, unique
from platform import version

import cv2
from PyQt6.QtMultimedia import QMediaDevices
from winsdk.windows.media.capture import MediaCapture

# https://docs.microsoft.com/en-us/uwp/api/windows.graphics.capture.graphicscapturepicker#applies-to
WCG_MIN_BUILD = 17134


def test_for_media_capture():
    async def coroutine():
        return await (MediaCapture().initialize_async() or asyncio.sleep(0))
    try:
        asyncio.run(coroutine())
        return True
    except OSError:
        return False


@dataclass
class DisplayCaptureMethodInfo():
    name: str
    short_description: str
    description: str


class CaptureMethodMeta(EnumMeta):
    # Allow checking if simple string is enum
    def __contains__(self, other: str):
        try:
            self(other)  # pyright: ignore [reportGeneralTypeIssues]
        except ValueError:
            return False
        else:
            return True


@unique
class CaptureMethod(Enum, metaclass=CaptureMethodMeta):
    # Allow TOML to save as a simple string
    def __repr__(self):
        return self.value
    __str__ = __repr__

    # Allow direct comparison with strings
    def __eq__(self, other: object):
        return self.value == other.__str__()

    # Restore hashing functionality
    def __hash__(self):
        return self.value.__hash__()

    BITBLT = "BITBLT"
    WINDOWS_GRAPHICS_CAPTURE = "WINDOWS_GRAPHICS_CAPTURE"
    PRINTWINDOW_RENDERFULLCONTENT = "PRINTWINDOW_RENDERFULLCONTENT"
    DESKTOP_DUPLICATION = "DESKTOP_DUPLICATION"
    VIDEO_CAPTURE_DEVICE = "VIDEO_CAPTURE_DEVICE"


class DisplayCaptureMethodDict(OrderedDict[CaptureMethod, DisplayCaptureMethodInfo]):
    def get_method_by_index(self, index: int):
        return list(self.keys())[index]


CAPTURE_METHODS = DisplayCaptureMethodDict({
    CaptureMethod.BITBLT: DisplayCaptureMethodInfo(
        name="BitBlt",
        short_description="fastest, least compatible",
        description=(
            "\nA good default fast option. Also allows recording background windows "
            "\n(as long as they still actually render when in the background), but it "
            "\ncannot properly record OpenGL, Hardware Accelerated or Exclusive Fullscreen windows. "
            "\nThe smaller the region, the more efficient it is. "
        ),
    ),
    CaptureMethod.WINDOWS_GRAPHICS_CAPTURE: DisplayCaptureMethodInfo(
        name="Windows Graphics Capture",
        short_description="fast, most compatible but less features",
        description=(
            f"\nOnly available in Windows 10.0.{WCG_MIN_BUILD} and up. "
            "\nDue to current technical limitations, it requires having at least one "
            "\naudio or video Capture Device connected and enabled. Even if it won't be used. "
            "\nAllows recording UWP apps, Hardware Accelerated and Exclusive Fullscreen windows. "
            "\nCaps at around 60 FPS. "
        ),
    ),
    CaptureMethod.DESKTOP_DUPLICATION: DisplayCaptureMethodInfo(
        name="Direct3D Desktop Duplication",
        short_description="slower, bound to display",
        description=(
            "\nDuplicates the desktop using Direct3D. "
            "\nIt can record OpenGL and Hardware Accelerated windows. "
            "\nAbout 10-15x slower than BitBlt. Not affected by window size. "
            "\noverlapping windows will show up and can't record across displays. "
        ),
    ),
    CaptureMethod.PRINTWINDOW_RENDERFULLCONTENT: DisplayCaptureMethodInfo(
        name="Force Full Content Rendering",
        short_description="very slow, can affect rendering pipeline",
        description=(
            "\nUses BitBlt behind the scene, but passes a special flag "
            "\nto PrintWindow to force rendering the entire desktop. "
            "\nAbout 10-15x slower than BitBlt based on original window size "
            "\nand can mess up some applications' rendering pipelines. "
        ),
    ),
    CaptureMethod.VIDEO_CAPTURE_DEVICE: DisplayCaptureMethodInfo(
        name="Video Capture Device",
        short_description="very slow, see below",
        description=(
            "\nUses a Video Capture Device, like a webcam, virtual cam, or capture card. "
            "\nYou can select one below. "
            "\nThere are currently performance issues, but it might be more convenient. "
            "\nIt is not yet possible for us to display the device name. "
            "\nIf you want to use this with OBS' Virtual Camera, use the Virtualcam plugin instead "
            "\nhttps://obsproject.com/forum/resources/obs-virtualcam.949/."
        ),
    ),
})


# Detect and remove unsupported capture methods
if (  # Windows Graphics Capture requires a minimum Windows Build
    int(version().split(".")[2]) < WCG_MIN_BUILD
    # Our current implementation of Windows Graphics Capture requires at least one CaptureDevice
    or not test_for_media_capture()
):
    CAPTURE_METHODS.pop(CaptureMethod.WINDOWS_GRAPHICS_CAPTURE)


@ dataclass
class CameraInfo():
    device_id: int
    name: str
    occupied: bool
    backend: str


async def get_all_video_capture_devices():
    named_video_inputs = [x.description() for x in QMediaDevices.videoInputs()]
    # Enough to ensure we catch "OBS-Camera" 1-4 (Virtualcam plugin) and "OBS Virtual Camera"
    device_range_to_test = range(len(named_video_inputs) + 5)

    async def get_camera_info(index: int):
        video_capture = cv2.VideoCapture(index)
        video_capture.setExceptionMode(True)
        backend = ""
        device_name = named_video_inputs[index] if index < len(named_video_inputs) else f"Camera {index}"
        try:
            # https://docs.opencv.org/3.4/d4/d15/group__videoio__flags__base.html#ga023786be1ee68a9105bf2e48c700294d
            backend = video_capture.getBackendName()
            video_capture.grab()
        except cv2.error as error:  # pyright: ignore [reportUnknownVariableType]
            return CameraInfo(index, device_name, True, backend) \
                if error.code == cv2.Error.STS_ERROR \
                else None
        finally:
            video_capture.release()
        return CameraInfo(index, device_name, False, backend)

    future = asyncio.gather(*[
        get_camera_info(index) for index
        in device_range_to_test
    ])

    return [
        camera_info for camera_info
        in await future
        if camera_info is not None]
