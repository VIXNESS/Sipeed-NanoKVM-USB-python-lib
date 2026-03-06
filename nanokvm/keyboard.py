"""
HID keyboard report builder and keycode mappings for NanoKVM-USB.

Produces standard 8-byte USB HID Boot Keyboard reports:
  [modifier_bitmap, 0x00, key1, key2, key3, key4, key5, key6]
"""

from __future__ import annotations

MAX_KEYS = 6

# ---------------------------------------------------------------------------
# Modifier key bit positions (byte 0 of the HID report)
# ---------------------------------------------------------------------------
MODIFIER_BITS: dict[str, int] = {
    "ControlLeft": 1 << 0,
    "ShiftLeft": 1 << 1,
    "AltLeft": 1 << 2,
    "MetaLeft": 1 << 3,
    "ControlRight": 1 << 4,
    "ShiftRight": 1 << 5,
    "AltRight": 1 << 6,
    "MetaRight": 1 << 7,
}

# Friendly aliases -> canonical event.code names
_MODIFIER_ALIASES: dict[str, str] = {
    "ctrl": "ControlLeft",
    "control": "ControlLeft",
    "shift": "ShiftLeft",
    "alt": "AltLeft",
    "meta": "MetaLeft",
    "win": "MetaLeft",
    "cmd": "MetaLeft",
    "super": "MetaLeft",
    "rctrl": "ControlRight",
    "rshift": "ShiftRight",
    "ralt": "AltRight",
    "rmeta": "MetaRight",
}

# ---------------------------------------------------------------------------
# event.code -> HID Usage ID (Usage Page 0x07)
# ---------------------------------------------------------------------------
KEYCODE_MAP: dict[str, int] = {
    # Letters
    "KeyA": 0x04,
    "KeyB": 0x05,
    "KeyC": 0x06,
    "KeyD": 0x07,
    "KeyE": 0x08,
    "KeyF": 0x09,
    "KeyG": 0x0A,
    "KeyH": 0x0B,
    "KeyI": 0x0C,
    "KeyJ": 0x0D,
    "KeyK": 0x0E,
    "KeyL": 0x0F,
    "KeyM": 0x10,
    "KeyN": 0x11,
    "KeyO": 0x12,
    "KeyP": 0x13,
    "KeyQ": 0x14,
    "KeyR": 0x15,
    "KeyS": 0x16,
    "KeyT": 0x17,
    "KeyU": 0x18,
    "KeyV": 0x19,
    "KeyW": 0x1A,
    "KeyX": 0x1B,
    "KeyY": 0x1C,
    "KeyZ": 0x1D,
    # Digits
    "Digit1": 0x1E,
    "Digit2": 0x1F,
    "Digit3": 0x20,
    "Digit4": 0x21,
    "Digit5": 0x22,
    "Digit6": 0x23,
    "Digit7": 0x24,
    "Digit8": 0x25,
    "Digit9": 0x26,
    "Digit0": 0x27,
    # Special keys
    "Enter": 0x28,
    "Escape": 0x29,
    "Backspace": 0x2A,
    "Tab": 0x2B,
    "Space": 0x2C,
    "Minus": 0x2D,
    "Equal": 0x2E,
    "BracketLeft": 0x2F,
    "BracketRight": 0x30,
    "Backslash": 0x31,
    "IntlHash": 0x32,
    "Semicolon": 0x33,
    "Quote": 0x34,
    "Backquote": 0x35,
    "Comma": 0x36,
    "Period": 0x37,
    "Slash": 0x38,
    "CapsLock": 0x39,
    # Function keys
    "F1": 0x3A,
    "F2": 0x3B,
    "F3": 0x3C,
    "F4": 0x3D,
    "F5": 0x3E,
    "F6": 0x3F,
    "F7": 0x40,
    "F8": 0x41,
    "F9": 0x42,
    "F10": 0x43,
    "F11": 0x44,
    "F12": 0x45,
    # Control keys
    "PrintScreen": 0x46,
    "ScrollLock": 0x47,
    "Pause": 0x48,
    "Insert": 0x49,
    "Home": 0x4A,
    "PageUp": 0x4B,
    "Delete": 0x4C,
    "End": 0x4D,
    "PageDown": 0x4E,
    # Arrow keys
    "ArrowRight": 0x4F,
    "ArrowLeft": 0x50,
    "ArrowDown": 0x51,
    "ArrowUp": 0x52,
    # Numpad
    "NumLock": 0x53,
    "NumpadDivide": 0x54,
    "NumpadMultiply": 0x55,
    "NumpadSubtract": 0x56,
    "NumpadAdd": 0x57,
    "NumpadEnter": 0x58,
    "Numpad1": 0x59,
    "Numpad2": 0x5A,
    "Numpad3": 0x5B,
    "Numpad4": 0x5C,
    "Numpad5": 0x5D,
    "Numpad6": 0x5E,
    "Numpad7": 0x5F,
    "Numpad8": 0x60,
    "Numpad9": 0x61,
    "Numpad0": 0x62,
    "NumpadDecimal": 0x63,
    # International
    "IntlBackslash": 0x64,
    "ContextMenu": 0x65,
    "Power": 0x66,
    "NumpadEqual": 0x67,
    # Extended function keys
    "F13": 0x68,
    "F14": 0x69,
    "F15": 0x6A,
    "F16": 0x6B,
    "F17": 0x6C,
    "F18": 0x6D,
    "F19": 0x6E,
    "F20": 0x6F,
    "F21": 0x70,
    "F22": 0x71,
    "F23": 0x72,
    "F24": 0x73,
    # System / Edit
    "Execute": 0x74,
    "Help": 0x75,
    "Props": 0x76,
    "Select": 0x77,
    "Stop": 0x78,
    "Again": 0x79,
    "Undo": 0x7A,
    "Cut": 0x7B,
    "Copy": 0x7C,
    "Paste": 0x7D,
    "Find": 0x7E,
    # Media / Volume
    "AudioVolumeMute": 0x7F,
    "AudioVolumeUp": 0x80,
    "AudioVolumeDown": 0x81,
    "VolumeMute": 0x7F,
    "VolumeUp": 0x80,
    "VolumeDown": 0x81,
    # Japanese keys
    "IntlRo": 0x87,
    "KanaMode": 0x88,
    "IntlYen": 0x89,
    "Convert": 0x8A,
    "NonConvert": 0x8B,
    # Language keys
    "Lang1": 0x90,
    "Lang2": 0x91,
    "Lang3": 0x92,
    "Lang4": 0x93,
    "Lang5": 0x94,
    # Numpad extended
    "NumpadParenLeft": 0xB6,
    "NumpadParenRight": 0xB7,
    "NumpadBackspace": 0xBB,
    "NumpadMemoryStore": 0xD0,
    "NumpadMemoryRecall": 0xD1,
    "NumpadMemoryClear": 0xD2,
    "NumpadMemoryAdd": 0xD3,
    "NumpadMemorySubtract": 0xD4,
    "NumpadClear": 0xD8,
    "NumpadClearEntry": 0xD9,
    # Media keys
    "MediaPlayPause": 0xE8,
    "MediaStop": 0xE9,
    "MediaTrackPrevious": 0xEA,
    "MediaTrackNext": 0xEB,
    "Eject": 0xEC,
    "MediaSelect": 0xED,
    # App launch
    "LaunchMail": 0xEE,
    "LaunchApp1": 0xEF,
    "LaunchApp2": 0xF0,
    # Browser keys
    "BrowserSearch": 0xF0,
    "BrowserHome": 0xF1,
    "BrowserBack": 0xF2,
    "BrowserForward": 0xF3,
    "BrowserStop": 0xF4,
    "BrowserRefresh": 0xF5,
    "BrowserFavorites": 0xF6,
    # Sleep / Wake / Accessibility
    "Sleep": 0xF8,
    "Wake": 0xF9,
    "MediaRewind": 0xFA,
    "MediaFastForward": 0xFB,
    # Modifier keycodes (HID 0xE0-0xE7)
    "ControlLeft": 0xE0,
    "ShiftLeft": 0xE1,
    "AltLeft": 0xE2,
    "MetaLeft": 0xE3,
    "WinLeft": 0xE3,
    "ControlRight": 0xE4,
    "ShiftRight": 0xE5,
    "AltRight": 0xE6,
    "MetaRight": 0xE7,
    "WinRight": 0xE7,
}

# Friendly key name aliases (case-insensitive lookup, see resolve_key_code())
_KEY_ALIASES: dict[str, str] = {
    "enter": "Enter",
    "return": "Enter",
    "esc": "Escape",
    "escape": "Escape",
    "backspace": "Backspace",
    "bs": "Backspace",
    "tab": "Tab",
    "space": "Space",
    "capslock": "CapsLock",
    "caps": "CapsLock",
    "delete": "Delete",
    "del": "Delete",
    "insert": "Insert",
    "ins": "Insert",
    "home": "Home",
    "end": "End",
    "pageup": "PageUp",
    "pgup": "PageUp",
    "pagedown": "PageDown",
    "pgdn": "PageDown",
    "up": "ArrowUp",
    "down": "ArrowDown",
    "left": "ArrowLeft",
    "right": "ArrowRight",
    "printscreen": "PrintScreen",
    "prtsc": "PrintScreen",
    "scrolllock": "ScrollLock",
    "pause": "Pause",
    "numlock": "NumLock",
    "f1": "F1",
    "f2": "F2",
    "f3": "F3",
    "f4": "F4",
    "f5": "F5",
    "f6": "F6",
    "f7": "F7",
    "f8": "F8",
    "f9": "F9",
    "f10": "F10",
    "f11": "F11",
    "f12": "F12",
    "minus": "Minus",
    "equal": "Equal",
    "bracketleft": "BracketLeft",
    "bracketright": "BracketRight",
    "backslash": "Backslash",
    "semicolon": "Semicolon",
    "quote": "Quote",
    "backquote": "Backquote",
    "comma": "Comma",
    "period": "Period",
    "slash": "Slash",
    "contextmenu": "ContextMenu",
    "menu": "ContextMenu",
}

# ---------------------------------------------------------------------------
# ASCII char -> (HID keycode, needs_shift)
# Used for type_text()
# ---------------------------------------------------------------------------
CHAR_CODES: dict[int, int] = {
    48: 0x27,
    49: 0x1E,
    50: 0x1F,
    51: 0x20,
    52: 0x21,
    53: 0x22,
    54: 0x23,
    55: 0x24,
    56: 0x25,
    57: 0x26,
    # A-Z
    65: 0x04,
    66: 0x05,
    67: 0x06,
    68: 0x07,
    69: 0x08,
    70: 0x09,
    71: 0x0A,
    72: 0x0B,
    73: 0x0C,
    74: 0x0D,
    75: 0x0E,
    76: 0x0F,
    77: 0x10,
    78: 0x11,
    79: 0x12,
    80: 0x13,
    81: 0x14,
    82: 0x15,
    83: 0x16,
    84: 0x17,
    85: 0x18,
    86: 0x19,
    87: 0x1A,
    88: 0x1B,
    89: 0x1C,
    90: 0x1D,
    # a-z
    97: 0x04,
    98: 0x05,
    99: 0x06,
    100: 0x07,
    101: 0x08,
    102: 0x09,
    103: 0x0A,
    104: 0x0B,
    105: 0x0C,
    106: 0x0D,
    107: 0x0E,
    108: 0x0F,
    109: 0x10,
    110: 0x11,
    111: 0x12,
    112: 0x13,
    113: 0x14,
    114: 0x15,
    115: 0x16,
    116: 0x17,
    117: 0x18,
    118: 0x19,
    119: 0x1A,
    120: 0x1B,
    121: 0x1C,
    122: 0x1D,
    # Symbols
    32: 0x2C,  # Space
    33: 0x1E,  # !
    34: 0x34,  # "
    35: 0x20,  # #
    36: 0x21,  # $
    37: 0x22,  # %
    38: 0x24,  # &
    39: 0x34,  # '
    40: 0x26,  # (
    41: 0x27,  # )
    42: 0x25,  # *
    43: 0x2E,  # +
    44: 0x36,  # ,
    45: 0x2D,  # -
    46: 0x37,  # .
    47: 0x38,  # /
    9: 0x2B,  # Tab
    10: 0x28,  # Enter (newline)
    58: 0x33,  # :
    59: 0x33,  # ;
    60: 0x36,  # <
    61: 0x2E,  # =
    62: 0x37,  # >
    63: 0x38,  # ?
    64: 0x1F,  # @
    91: 0x2F,  # [
    92: 0x31,  # backslash
    93: 0x30,  # ]
    94: 0x23,  # ^
    95: 0x2D,  # _
    96: 0x35,  # `
    123: 0x2F,  # {
    124: 0x31,  # |
    125: 0x30,  # }
    126: 0x35,  # ~
}

SHIFT_CHARS: set[int] = {
    33,
    64,
    35,
    36,
    37,
    94,
    38,
    42,
    40,
    41,  # ! @ # $ % ^ & * ( )
    95,
    43,  # _ +
    123,
    124,
    125,  # { | }
    58,
    34,
    126,  # : " ~
    60,
    62,
    63,  # < > ?
}


def _is_upper(char_code: int) -> bool:
    return 65 <= char_code <= 90


def resolve_key_code(name: str) -> str:
    """Resolve a friendly key name to a canonical event.code string."""
    if name in KEYCODE_MAP or name in MODIFIER_BITS:
        return name
    lower = name.lower()
    if lower in _KEY_ALIASES:
        return _KEY_ALIASES[lower]
    if lower in _MODIFIER_ALIASES:
        return _MODIFIER_ALIASES[lower]
    if len(name) == 1:
        c = name.upper()
        if "A" <= c <= "Z":
            return f"Key{c}"
        if "0" <= c <= "9":
            return f"Digit{c}"
    raise ValueError(f"Unknown key: {name!r}")


def is_modifier(code: str) -> bool:
    return code in MODIFIER_BITS


class KeyboardReport:
    """Builds 8-byte HID keyboard reports, tracking pressed keys and modifiers."""

    def __init__(self) -> None:
        self._modifier: int = 0
        self._pressed: dict[str, int] = {}  # code -> keycode

    def key_down(self, code: str) -> list[int]:
        if is_modifier(code):
            self._modifier |= MODIFIER_BITS[code]
        else:
            keycode = KEYCODE_MAP.get(code)
            if keycode is not None and len(self._pressed) < MAX_KEYS:
                self._pressed[code] = keycode
        return self._build_report()

    def key_up(self, code: str) -> list[int]:
        if is_modifier(code):
            self._modifier &= ~MODIFIER_BITS[code]
        else:
            self._pressed.pop(code, None)
        return self._build_report()

    def reset(self) -> list[int]:
        self._modifier = 0
        self._pressed.clear()
        return self._build_report()

    def _build_report(self) -> list[int]:
        report = [self._modifier, 0, 0, 0, 0, 0, 0, 0]
        for i, keycode in enumerate(self._pressed.values()):
            if i >= MAX_KEYS:
                break
            report[2 + i] = keycode
        return report

    def char_to_report(self, ch: str) -> tuple[list[int], list[int]]:
        """
        Convert a single ASCII character to (key_down_report, key_up_report).
        Returns the pair for sending a press-then-release.
        """
        code = ord(ch)
        hid_code = CHAR_CODES.get(code)
        if hid_code is None:
            raise ValueError(f"Unsupported character: {ch!r} (0x{code:02X})")

        needs_shift = code in SHIFT_CHARS or _is_upper(code)
        modifier = MODIFIER_BITS["ShiftLeft"] if needs_shift else 0

        down = [modifier, 0, hid_code, 0, 0, 0, 0, 0]
        up = [0, 0, 0, 0, 0, 0, 0, 0]
        return down, up
