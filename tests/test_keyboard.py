from __future__ import annotations

import pytest

from nanokvm.keyboard import (
    KEYCODE_MAP,
    MODIFIER_BITS,
    KeyboardReport,
    is_modifier,
    resolve_key_code,
)


class TestResolveKeyCode:
    def test_canonical_keycode_passthrough(self) -> None:
        assert resolve_key_code("Enter") == "Enter"
        assert resolve_key_code("KeyA") == "KeyA"
        assert resolve_key_code("F1") == "F1"
        assert resolve_key_code("ArrowUp") == "ArrowUp"

    def test_canonical_modifier_passthrough(self) -> None:
        assert resolve_key_code("ControlLeft") == "ControlLeft"
        assert resolve_key_code("ShiftLeft") == "ShiftLeft"

    def test_friendly_key_aliases(self) -> None:
        assert resolve_key_code("enter") == "Enter"
        assert resolve_key_code("esc") == "Escape"
        assert resolve_key_code("backspace") == "Backspace"
        assert resolve_key_code("tab") == "Tab"
        assert resolve_key_code("space") == "Space"
        assert resolve_key_code("del") == "Delete"
        assert resolve_key_code("pgup") == "PageUp"
        assert resolve_key_code("up") == "ArrowUp"

    def test_friendly_modifier_aliases(self) -> None:
        assert resolve_key_code("ctrl") == "ControlLeft"
        assert resolve_key_code("shift") == "ShiftLeft"
        assert resolve_key_code("alt") == "AltLeft"
        assert resolve_key_code("meta") == "MetaLeft"
        assert resolve_key_code("win") == "MetaLeft"
        assert resolve_key_code("cmd") == "MetaLeft"
        assert resolve_key_code("rctrl") == "ControlRight"

    def test_single_letter_resolution(self) -> None:
        assert resolve_key_code("a") == "KeyA"
        assert resolve_key_code("z") == "KeyZ"
        assert resolve_key_code("A") == "KeyA"

    def test_single_digit_resolution(self) -> None:
        assert resolve_key_code("0") == "Digit0"
        assert resolve_key_code("5") == "Digit5"
        assert resolve_key_code("9") == "Digit9"

    def test_unknown_key_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown key"):
            resolve_key_code("nonexistent_key")

    def test_case_insensitive_aliases(self) -> None:
        assert resolve_key_code("ENTER") == "Enter"
        assert resolve_key_code("Enter") == "Enter"
        assert resolve_key_code("CTRL") == "ControlLeft"


class TestIsModifier:
    def test_modifier_keys(self) -> None:
        for mod_code in MODIFIER_BITS:
            assert is_modifier(mod_code) is True

    def test_non_modifier_keys(self) -> None:
        assert is_modifier("Enter") is False
        assert is_modifier("KeyA") is False
        assert is_modifier("Space") is False


class TestKeyboardReport:
    def test_initial_report_is_zeros(self) -> None:
        kb = KeyboardReport()
        report = kb.reset()
        assert report == [0, 0, 0, 0, 0, 0, 0, 0]

    def test_report_length(self) -> None:
        kb = KeyboardReport()
        report = kb.key_down("KeyA")
        assert len(report) == 8

    def test_regular_key_down(self) -> None:
        kb = KeyboardReport()
        report = kb.key_down("KeyA")
        assert report[0] == 0  # no modifiers
        assert report[1] == 0  # reserved
        assert report[2] == KEYCODE_MAP["KeyA"]

    def test_regular_key_up(self) -> None:
        kb = KeyboardReport()
        kb.key_down("KeyA")
        report = kb.key_up("KeyA")
        assert report == [0, 0, 0, 0, 0, 0, 0, 0]

    def test_modifier_key_down(self) -> None:
        kb = KeyboardReport()
        report = kb.key_down("ShiftLeft")
        assert report[0] == MODIFIER_BITS["ShiftLeft"]
        assert report[2:] == [0, 0, 0, 0, 0, 0]

    def test_modifier_key_up(self) -> None:
        kb = KeyboardReport()
        kb.key_down("ShiftLeft")
        report = kb.key_up("ShiftLeft")
        assert report[0] == 0

    def test_multiple_modifiers(self) -> None:
        kb = KeyboardReport()
        kb.key_down("ControlLeft")
        report = kb.key_down("AltLeft")
        expected = MODIFIER_BITS["ControlLeft"] | MODIFIER_BITS["AltLeft"]
        assert report[0] == expected

    def test_multiple_keys(self) -> None:
        kb = KeyboardReport()
        kb.key_down("KeyA")
        report = kb.key_down("KeyB")
        assert report[2] == KEYCODE_MAP["KeyA"]
        assert report[3] == KEYCODE_MAP["KeyB"]

    def test_max_six_keys(self) -> None:
        kb = KeyboardReport()
        keys = ["KeyA", "KeyB", "KeyC", "KeyD", "KeyE", "KeyF"]
        for k in keys:
            kb.key_down(k)
        report = kb.key_down("KeyG")  # 7th key, should be ignored
        for i, k in enumerate(keys):
            assert report[2 + i] == KEYCODE_MAP[k]

    def test_reset_clears_all(self) -> None:
        kb = KeyboardReport()
        kb.key_down("ShiftLeft")
        kb.key_down("KeyA")
        report = kb.reset()
        assert report == [0, 0, 0, 0, 0, 0, 0, 0]


class TestCharToReport:
    def test_lowercase_letter(self) -> None:
        kb = KeyboardReport()
        down, up = kb.char_to_report("a")
        assert down[0] == 0  # no shift
        assert down[2] == KEYCODE_MAP["KeyA"]
        assert up == [0, 0, 0, 0, 0, 0, 0, 0]

    def test_uppercase_letter(self) -> None:
        kb = KeyboardReport()
        down, up = kb.char_to_report("A")
        assert down[0] == MODIFIER_BITS["ShiftLeft"]
        assert down[2] == KEYCODE_MAP["KeyA"]

    def test_digit(self) -> None:
        kb = KeyboardReport()
        down, _up = kb.char_to_report("5")
        assert down[0] == 0
        assert down[2] == 0x22  # Digit5 HID code

    def test_space(self) -> None:
        kb = KeyboardReport()
        down, _up = kb.char_to_report(" ")
        assert down[0] == 0
        assert down[2] == 0x2C  # Space HID code

    def test_shift_symbol(self) -> None:
        kb = KeyboardReport()
        down, _up = kb.char_to_report("!")
        assert down[0] == MODIFIER_BITS["ShiftLeft"]

    def test_unsupported_char_raises(self) -> None:
        kb = KeyboardReport()
        with pytest.raises(ValueError, match="Unsupported character"):
            kb.char_to_report("\x80")

    def test_report_lengths(self) -> None:
        kb = KeyboardReport()
        down, up = kb.char_to_report("x")
        assert len(down) == 8
        assert len(up) == 8
