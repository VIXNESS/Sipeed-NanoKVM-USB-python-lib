"""
HID mouse report builders for NanoKVM-USB.

Supports both absolute and relative mouse modes:
- Absolute: 7-byte report [0x02, buttons, x_lo, x_hi, y_lo, y_hi, wheel]
- Relative: 5-byte report [0x01, buttons, dx, dy, wheel]
"""

from __future__ import annotations

MAX_ABS_COORD = 4096

MOUSE_MODE_RELATIVE = 0x01
MOUSE_MODE_ABSOLUTE = 0x02


class MouseButton:
    LEFT = 1 << 0
    RIGHT = 1 << 1
    MIDDLE = 1 << 2
    BACK = 1 << 3
    FORWARD = 1 << 4


_BUTTON_NAMES: dict[str, int] = {
    "left": MouseButton.LEFT,
    "right": MouseButton.RIGHT,
    "middle": MouseButton.MIDDLE,
    "back": MouseButton.BACK,
    "forward": MouseButton.FORWARD,
}


def resolve_button(button: str | int) -> int:
    if isinstance(button, int):
        return button
    name = button.lower()
    if name not in _BUTTON_NAMES:
        raise ValueError(f"Unknown mouse button: {button!r}")
    return _BUTTON_NAMES[name]


def _clamp(value: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, value))


def _to_signed_byte(value: int) -> int:
    """Convert a signed int (-127..127) to an unsigned byte for the report."""
    return _clamp(value, -127, 127) & 0xFF


def build_absolute_report(
    x: float,
    y: float,
    buttons: int = 0,
    wheel: int = 0,
) -> list[int]:
    """
    Build a 7-byte absolute mouse report.

    Args:
        x: Normalized X position (0.0 to 1.0)
        y: Normalized Y position (0.0 to 1.0)
        buttons: Button bitmap
        wheel: Scroll wheel (-127 to 127, negative = down)
    """
    x_abs = int(max(0.0, min(1.0, x)) * MAX_ABS_COORD)
    y_abs = int(max(0.0, min(1.0, y)) * MAX_ABS_COORD)
    return [
        MOUSE_MODE_ABSOLUTE,
        buttons,
        x_abs & 0xFF,
        (x_abs >> 8) & 0xFF,
        y_abs & 0xFF,
        (y_abs >> 8) & 0xFF,
        _to_signed_byte(wheel),
    ]


def build_relative_report(
    dx: int = 0,
    dy: int = 0,
    buttons: int = 0,
    wheel: int = 0,
) -> list[int]:
    """
    Build a 5-byte relative mouse report.

    Args:
        dx: X movement (-127 to 127)
        dy: Y movement (-127 to 127)
        buttons: Button bitmap
        wheel: Scroll wheel (-127 to 127, negative = down)
    """
    return [
        MOUSE_MODE_RELATIVE,
        buttons,
        _to_signed_byte(dx),
        _to_signed_byte(dy),
        _to_signed_byte(wheel),
    ]
