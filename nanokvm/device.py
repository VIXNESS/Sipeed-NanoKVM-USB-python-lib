"""
High-level NanoKVM device API combining serial (keyboard/mouse) and video capture.

Designed for AI agent integration: simple methods for screen capture,
keyboard input, and mouse control.
"""

from __future__ import annotations

import time

from .keyboard import KeyboardReport, resolve_key_code
from .mouse import (
    build_absolute_report,
    build_relative_report,
    resolve_button,
)
from .protocol import CmdEvent, CmdPacket, InfoPacket
from .serial_conn import SerialConnection
from .video import VideoCapture

import numpy as np
from numpy.typing import NDArray

INTER_KEY_DELAY = 0.05
KEY_HOLD_DELAY = 0.02


class NanoKVM:
    """
    Unified interface to a NanoKVM-USB device.

    Typical usage::

        from nanokvm import NanoKVM

        kvm = NanoKVM(serial_port="/dev/ttyACM0", video_device=0)
        kvm.connect()

        info = kvm.get_info()
        frame = kvm.capture_frame()

        kvm.type_text("hello")
        kvm.press_key("Enter")
        kvm.key_combo(["ctrl", "c"])
        kvm.mouse_click(0.5, 0.5)

        kvm.disconnect()
    """

    def __init__(
        self,
        serial_port: str | None = None,
        baud_rate: int = 57600,
        video_device: int | str | None = None,
        video_width: int = 1920,
        video_height: int = 1080,
        video_fps: int = 30,
    ) -> None:
        self._serial_port_path = serial_port
        self._baud_rate = baud_rate
        self._video_device = video_device
        self._video_width = video_width
        self._video_height = video_height
        self._video_fps = video_fps

        self._serial = SerialConnection()
        self._video = VideoCapture()
        self._keyboard = KeyboardReport()
        self._addr = 0x00
        self._buttons = 0  # current mouse button state

    # ------------------------------------------------------------------
    # Connection management
    # ------------------------------------------------------------------

    def connect(
        self,
        serial_port: str | None = None,
        video_device: int | str | None = None,
    ) -> InfoPacket | None:
        """
        Open serial and/or video connections.
        Returns device info if serial is connected, None otherwise.
        """
        port = serial_port or self._serial_port_path
        vdev = video_device if video_device is not None else self._video_device

        info = None
        if port is not None:
            self._serial.open(port, self._baud_rate)
            info = self.get_info()

        if vdev is not None:
            self._video.open(
                vdev, self._video_width, self._video_height, self._video_fps
            )

        return info

    def disconnect(self) -> None:
        self._serial.close()
        self._video.close()

    @property
    def is_connected(self) -> bool:
        return self._serial.is_open

    @property
    def has_video(self) -> bool:
        return self._video.is_open

    # ------------------------------------------------------------------
    # Device info
    # ------------------------------------------------------------------

    def get_info(self) -> InfoPacket:
        """Query device info (version, connected state, lock LEDs)."""
        pkt = CmdPacket(addr=self._addr, cmd=CmdEvent.GET_INFO)
        self._serial.write(pkt.encode())
        rsp = self._serial.read(14)
        rsp_pkt = CmdPacket.decode(rsp)
        return InfoPacket.from_data(rsp_pkt.data)

    # ------------------------------------------------------------------
    # Keyboard
    # ------------------------------------------------------------------

    def _send_keyboard(self, report: list[int]) -> None:
        pkt = CmdPacket(addr=self._addr, cmd=CmdEvent.SEND_KB_GENERAL_DATA, data=report)
        self._serial.write(pkt.encode())

    def press_key(self, key: str, hold: float = KEY_HOLD_DELAY) -> None:
        """
        Press and release a single key.

        Args:
            key: Key name -- can be event.code ("KeyA", "Enter") or a friendly
                 name ("a", "enter", "f1", "ctrl", "shift").
            hold: Seconds to hold the key before releasing.
        """
        code = resolve_key_code(key)
        report = self._keyboard.key_down(code)
        self._send_keyboard(report)
        time.sleep(hold)
        report = self._keyboard.key_up(code)
        self._send_keyboard(report)

    def key_down(self, key: str) -> None:
        """Press a key without releasing it."""
        code = resolve_key_code(key)
        report = self._keyboard.key_down(code)
        self._send_keyboard(report)

    def key_up(self, key: str) -> None:
        """Release a previously pressed key."""
        code = resolve_key_code(key)
        report = self._keyboard.key_up(code)
        self._send_keyboard(report)

    def key_combo(self, keys: list[str], hold: float = KEY_HOLD_DELAY) -> None:
        """
        Press a key combination (e.g. Ctrl+C) and release.

        Args:
            keys: List of key names, e.g. ["ctrl", "c"] or ["ctrl", "shift", "s"].
            hold: Seconds to hold before releasing.
        """
        codes = [resolve_key_code(k) for k in keys]
        for code in codes:
            report = self._keyboard.key_down(code)
            self._send_keyboard(report)
        time.sleep(hold)
        for code in reversed(codes):
            report = self._keyboard.key_up(code)
            self._send_keyboard(report)

    def release_all_keys(self) -> None:
        """Release all pressed keys and modifiers."""
        report = self._keyboard.reset()
        self._send_keyboard(report)

    def type_text(self, text: str, delay: float = INTER_KEY_DELAY) -> None:
        """
        Type a string of ASCII characters one by one.

        Args:
            text: The text to type (ASCII printable characters).
            delay: Delay between each keystroke in seconds.
        """
        for ch in text:
            down, up = self._keyboard.char_to_report(ch)
            self._send_keyboard(down)
            time.sleep(KEY_HOLD_DELAY)
            self._send_keyboard(up)
            time.sleep(delay)

    # ------------------------------------------------------------------
    # Mouse
    # ------------------------------------------------------------------

    def _send_mouse(self, report: list[int]) -> None:
        pkt_cmd = (
            CmdEvent.SEND_MS_REL_DATA
            if report[0] == 0x01
            else CmdEvent.SEND_MS_ABS_DATA
        )
        pkt = CmdPacket(addr=self._addr, cmd=pkt_cmd, data=report)
        self._serial.write(pkt.encode())

    def mouse_move(self, x: float, y: float) -> None:
        """
        Move the mouse to an absolute position (absolute mode).

        Args:
            x: Normalized X position (0.0 = left, 1.0 = right).
            y: Normalized Y position (0.0 = top, 1.0 = bottom).
        """
        report = build_absolute_report(x, y, buttons=self._buttons)
        self._send_mouse(report)

    def mouse_click(
        self,
        x: float | None = None,
        y: float | None = None,
        button: str | int = "left",
        hold: float = 0.05,
    ) -> None:
        """
        Click at an absolute position.

        Args:
            x: Normalized X (0.0-1.0). If None, click in place (relative mode).
            y: Normalized Y (0.0-1.0). If None, click in place (relative mode).
            button: Button name ("left", "right", "middle") or bit value.
            hold: Seconds to hold button down.
        """
        btn_bit = resolve_button(button)

        if x is not None and y is not None:
            self._buttons |= btn_bit
            report = build_absolute_report(x, y, buttons=self._buttons)
            self._send_mouse(report)
            time.sleep(hold)
            self._buttons &= ~btn_bit
            report = build_absolute_report(x, y, buttons=self._buttons)
            self._send_mouse(report)
        else:
            self._buttons |= btn_bit
            report = build_relative_report(buttons=self._buttons)
            self._send_mouse(report)
            time.sleep(hold)
            self._buttons &= ~btn_bit
            report = build_relative_report(buttons=self._buttons)
            self._send_mouse(report)

    def mouse_double_click(
        self,
        x: float | None = None,
        y: float | None = None,
        button: str | int = "left",
        interval: float = 0.1,
    ) -> None:
        """Double-click at a position."""
        self.mouse_click(x, y, button)
        time.sleep(interval)
        self.mouse_click(x, y, button)

    def mouse_move_relative(self, dx: int, dy: int, step_delay: float = 0.005) -> None:
        """
        Move the mouse by a relative offset.

        Accepts any integer distance; large moves are automatically split
        into multiple -127/+127 HID reports.

        Args:
            dx: Horizontal movement in pixels (any integer).
            dy: Vertical movement in pixels (any integer).
            step_delay: Seconds between chunked reports.
        """
        while dx != 0 or dy != 0:
            chunk_x = max(-127, min(127, dx))
            chunk_y = max(-127, min(127, dy))
            report = build_relative_report(
                dx=chunk_x, dy=chunk_y, buttons=self._buttons
            )
            self._send_mouse(report)
            dx -= chunk_x
            dy -= chunk_y
            if dx != 0 or dy != 0:
                time.sleep(step_delay)

    def mouse_move_to(
        self,
        x: float,
        y: float,
        screen_width: int = 1920,
        screen_height: int = 1080,
    ) -> None:
        """
        Move the mouse to a screen position using relative mode.

        Works by first resetting the cursor to the top-left corner, then
        moving to the target pixel position. Use this when absolute mode
        fails at screen edges.

        Args:
            x: Normalized X position (0.0 = left, 1.0 = right).
            y: Normalized Y position (0.0 = top, 1.0 = bottom).
            screen_width: Target screen width in pixels.
            screen_height: Target screen height in pixels.
        """
        self.mouse_move_relative(-screen_width * 2, -screen_height * 2)
        target_x = int(x * screen_width)
        target_y = int(y * screen_height)
        self.mouse_move_relative(target_x, target_y)

    def mouse_scroll(self, delta: int) -> None:
        """
        Scroll the mouse wheel.

        Args:
            delta: Scroll amount (-127 to 127, negative = down).
        """
        report = build_relative_report(wheel=delta, buttons=self._buttons)
        self._send_mouse(report)

    def mouse_button_down(self, button: str | int = "left") -> None:
        self._buttons |= resolve_button(button)
        report = build_relative_report(buttons=self._buttons)
        self._send_mouse(report)

    def mouse_button_up(self, button: str | int = "left") -> None:
        self._buttons &= ~resolve_button(button)
        report = build_relative_report(buttons=self._buttons)
        self._send_mouse(report)

    def mouse_reset(self) -> None:
        """Release all mouse buttons."""
        self._buttons = 0
        report = build_relative_report(buttons=0)
        self._send_mouse(report)

    # ------------------------------------------------------------------
    # Video capture
    # ------------------------------------------------------------------

    def capture_frame(self) -> NDArray[np.uint8]:
        """
        Capture a single video frame as a BGR numpy array.

        Returns:
            numpy array of shape (height, width, 3) in BGR color order.
        """
        return self._video.read_frame()

    def capture_frame_rgb(self) -> NDArray[np.uint8]:
        """Capture a frame in RGB color order."""
        return self._video.read_frame_rgb()

    def capture_frame_jpeg(self, quality: int = 85) -> bytes:
        """Capture a frame as JPEG bytes."""
        return self._video.read_frame_jpeg(quality)

    def capture_frame_base64(self, quality: int = 85) -> str:
        """
        Capture a frame as a base64-encoded JPEG string.
        Ready to send to multimodal LLM APIs (OpenAI, Anthropic, etc.).
        """
        return self._video.read_frame_base64(quality)

    def get_video_resolution(self) -> tuple[int, int]:
        return self._video.get_resolution()

    # ------------------------------------------------------------------
    # Context manager
    # ------------------------------------------------------------------

    def __enter__(self) -> NanoKVM:
        self.connect()
        return self

    def __exit__(self, *_: object) -> None:
        self.disconnect()

    def __repr__(self) -> str:
        return (
            f"NanoKVM(serial={self._serial_port_path!r}, "
            f"video={self._video_device!r}, "
            f"connected={self.is_connected})"
        )
