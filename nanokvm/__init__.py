"""
nanokvm - Python library for controlling machines via NanoKVM-USB.

Provides serial-based keyboard/mouse HID control and UVC video capture,
designed for AI agent integration.

Quick start::

    from nanokvm import NanoKVM

    kvm = NanoKVM(serial_port="/dev/ttyACM0", video_device=0)
    kvm.connect()

    frame = kvm.capture_frame_base64()   # for LLM vision APIs
    kvm.type_text("hello world")
    kvm.press_key("Enter")
    kvm.mouse_click(0.5, 0.5)

    kvm.disconnect()
"""

from .device import NanoKVM
from .keyboard import KeyboardReport
from .mouse import MouseButton, build_absolute_report, build_relative_report
from .protocol import CmdEvent, CmdPacket, InfoPacket
from .serial_conn import SerialConnection
from .video import VideoCapture

__version__ = "0.1.2"

__all__ = [
    "NanoKVM",
    "CmdEvent",
    "CmdPacket",
    "InfoPacket",
    "SerialConnection",
    "VideoCapture",
    "KeyboardReport",
    "MouseButton",
    "build_absolute_report",
    "build_relative_report",
]
