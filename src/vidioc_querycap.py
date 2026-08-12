# ruff: noqa: E501 # Copied long descriptions
"""
Implements https://www.kernel.org/doc/html/latest/userspace-api/media/v4l/vidioc-querycap.html .
Avoids dependency on https://tiagocoutinho.github.io/linuxpy/api/video/?h=#linuxpy.video.device.iter_devices .
"""

import ctypes


class v4l2_capability(ctypes.Structure):  # noqa: N801
    """https://www.kernel.org/doc/html/latest/userspace-api/media/v4l/vidioc-querycap.html#c.V4L.v4l2_capability"""  # noqa: D400, D415

    driver: bytes  # pyright: ignore[reportUninitializedInstanceVariable]
    card: bytes  # pyright: ignore[reportUninitializedInstanceVariable]
    bus_info: bytes  # pyright: ignore[reportUninitializedInstanceVariable]
    version: int  # pyright: ignore[reportUninitializedInstanceVariable]
    capabilities: int  # pyright: ignore[reportUninitializedInstanceVariable]
    device_caps: int  # pyright: ignore[reportUninitializedInstanceVariable]

    _fields_ = [
        ("driver", ctypes.c_char * 16),
        ("card", ctypes.c_char * 32),
        ("bus_info", ctypes.c_char * 32),
        ("version", ctypes.c_uint32),
        ("capabilities", ctypes.c_uint32),
        ("device_caps", ctypes.c_uint32),
        ("reserved", ctypes.c_uint32 * 3),
    ]


VIDIOC_QUERYCAP = 0x80685600
"""ioctl ID, example here: https://github.com/jerome-pouiller/ioctl
Part of stable ABI, so should not change."""

###
# Device Capabilities Flags
###
V4L2_CAP_VIDEO_CAPTURE = 0x00000001
"""The device supports the single-planar API through the Video Capture interface."""
V4L2_CAP_VIDEO_CAPTURE_MPLANE = 0x00001000
"""The device supports the multi-planar API through the Video Capture interface."""
V4L2_CAP_VIDEO_OUTPUT = 0x00000002
"""The device supports the single-planar API through the Video Output interface."""
V4L2_CAP_VIDEO_OUTPUT_MPLANE = 0x00002000
"""The device supports the multi-planar API through the Video Output interface."""
V4L2_CAP_VIDEO_M2M = 0x00008000
"""The device supports the single-planar API through the Video Memory-To-Memory interface."""
V4L2_CAP_VIDEO_M2M_MPLANE = 0x00004000
"""The device supports the multi-planar API through the Video Memory-To-Memory interface."""
V4L2_CAP_VIDEO_OVERLAY = 0x00000004
"""The device supports the Video Overlay interface. A video overlay device typically stores captured images directly in the video memory of a graphics card, with hardware clipping and scaling."""
V4L2_CAP_VBI_CAPTURE = 0x00000010
"""The device supports the Raw VBI Capture interface, providing Teletext and Closed Caption data."""
V4L2_CAP_VBI_OUTPUT = 0x00000020
"""The device supports the Raw VBI Output interface."""
V4L2_CAP_SLICED_VBI_CAPTURE = 0x00000040
"""The device supports the Sliced VBI Capture interface."""
V4L2_CAP_SLICED_VBI_OUTPUT = 0x00000080
"""The device supports the Sliced VBI Output interface."""
V4L2_CAP_RDS_CAPTURE = 0x00000100
"""The device supports the RDS capture interface."""
V4L2_CAP_VIDEO_OUTPUT_OVERLAY = 0x00000200
"""The device supports the Video Output Overlay (OSD) interface. Unlike the Video Overlay interface, this is a secondary function of video output devices and overlays an image onto an outgoing video signal. When the driver sets this flag, it must clear the V4L2_CAP_VIDEO_OVERLAY flag and vice versa. [1]"""
V4L2_CAP_HW_FREQ_SEEK = 0x00000400
"""The device supports the ioctl VIDIOC_S_HW_FREQ_SEEK ioctl for hardware frequency seeking."""
V4L2_CAP_RDS_OUTPUT = 0x00000800
"""The device supports the RDS output interface."""
V4L2_CAP_TUNER = 0x00010000
"""The device has some sort of tuner to receive RF-modulated video signals. For more information about tuner programming see Tuners and Modulators."""
V4L2_CAP_AUDIO = 0x00020000
"""The device has audio inputs or outputs. It may or may not support audio recording or playback, in PCM or compressed formats. PCM audio support must be implemented as ALSA or OSS interface. For more information on audio inputs and outputs see Audio Inputs and Outputs."""
V4L2_CAP_RADIO = 0x00040000
"""This is a radio receiver."""
V4L2_CAP_MODULATOR = 0x00080000
"""The device has some sort of modulator to emit RF-modulated video/audio signals. For more information about modulator programming see Tuners and Modulators."""
V4L2_CAP_SDR_CAPTURE = 0x00100000
"""The device supports the SDR Capture interface."""
V4L2_CAP_EXT_PIX_FORMAT = 0x00200000
"""The device supports the struct v4l2_pix_format extended fields."""
V4L2_CAP_SDR_OUTPUT = 0x00400000
"""The device supports the SDR Output interface."""
V4L2_CAP_META_CAPTURE = 0x00800000
"""The device supports the Metadata Interface capture interface."""
V4L2_CAP_READWRITE = 0x01000000
"""The device supports the read() and/or write() I/O methods."""
V4L2_CAP_EDID = 0x02000000
"""
The device stores the EDID for a video input, or retrieves the EDID for a video output. It is a standalone EDID device, so no video streaming etc. will take place.

For a video input this is typically an eeprom that supports the VESA Enhanced Display Data Channel Standard. It can be something else as well, for example a micro controller.

For a video output this is typically read from an external device such as an HDMI splitter accessed by a serial port.
"""
V4L2_CAP_STREAMING = 0x04000000
"""The device supports the streaming I/O method."""
V4L2_CAP_META_OUTPUT = 0x08000000
"""The device supports the Metadata Interface output interface."""
V4L2_CAP_TOUCH = 0x10000000
"""This is a touch device."""
V4L2_CAP_IO_MC = 0x20000000
"""There is only one input and/or output seen from userspace. The whole video topology configuration, including which I/O entity is routed to the input/output, is configured by userspace via the Media Controller. See Part IV - Media Controller API."""
V4L2_CAP_DEVICE_CAPS = 0x80000000
"""The driver fills the device_caps field. This capability can only appear in the capabilities field and never in the device_caps field."""
