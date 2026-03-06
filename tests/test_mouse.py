from __future__ import annotations

import pytest

from nanokvm.mouse import (
    MAX_ABS_COORD,
    MOUSE_MODE_ABSOLUTE,
    MOUSE_MODE_RELATIVE,
    MouseButton,
    build_absolute_report,
    build_relative_report,
    resolve_button,
)


class TestMouseButton:
    def test_bit_positions(self) -> None:
        assert MouseButton.LEFT == 0x01
        assert MouseButton.RIGHT == 0x02
        assert MouseButton.MIDDLE == 0x04
        assert MouseButton.BACK == 0x08
        assert MouseButton.FORWARD == 0x10


class TestResolveButton:
    def test_string_names(self) -> None:
        assert resolve_button("left") == MouseButton.LEFT
        assert resolve_button("right") == MouseButton.RIGHT
        assert resolve_button("middle") == MouseButton.MIDDLE
        assert resolve_button("back") == MouseButton.BACK
        assert resolve_button("forward") == MouseButton.FORWARD

    def test_case_insensitive(self) -> None:
        assert resolve_button("LEFT") == MouseButton.LEFT
        assert resolve_button("Right") == MouseButton.RIGHT

    def test_int_passthrough(self) -> None:
        assert resolve_button(0x01) == 0x01
        assert resolve_button(42) == 42

    def test_unknown_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown mouse button"):
            resolve_button("invalid")


class TestBuildAbsoluteReport:
    def test_report_length(self) -> None:
        report = build_absolute_report(0.5, 0.5)
        assert len(report) == 7

    def test_mode_byte(self) -> None:
        report = build_absolute_report(0.0, 0.0)
        assert report[0] == MOUSE_MODE_ABSOLUTE

    def test_origin(self) -> None:
        report = build_absolute_report(0.0, 0.0)
        assert report[2] == 0  # x_lo
        assert report[3] == 0  # x_hi
        assert report[4] == 0  # y_lo
        assert report[5] == 0  # y_hi

    def test_max_position(self) -> None:
        report = build_absolute_report(1.0, 1.0)
        x = report[2] | (report[3] << 8)
        y = report[4] | (report[5] << 8)
        assert x == MAX_ABS_COORD
        assert y == MAX_ABS_COORD

    def test_center_position(self) -> None:
        report = build_absolute_report(0.5, 0.5)
        x = report[2] | (report[3] << 8)
        y = report[4] | (report[5] << 8)
        assert x == MAX_ABS_COORD // 2
        assert y == MAX_ABS_COORD // 2

    def test_buttons(self) -> None:
        report = build_absolute_report(0.0, 0.0, buttons=MouseButton.LEFT)
        assert report[1] == MouseButton.LEFT

    def test_wheel(self) -> None:
        report = build_absolute_report(0.0, 0.0, wheel=5)
        assert report[6] == 5

    def test_negative_wheel(self) -> None:
        report = build_absolute_report(0.0, 0.0, wheel=-5)
        assert report[6] == (-5) & 0xFF

    def test_clamp_below_zero(self) -> None:
        report = build_absolute_report(-0.5, -0.5)
        assert report[2] == 0
        assert report[3] == 0

    def test_clamp_above_one(self) -> None:
        report = build_absolute_report(1.5, 1.5)
        x = report[2] | (report[3] << 8)
        y = report[4] | (report[5] << 8)
        assert x == MAX_ABS_COORD
        assert y == MAX_ABS_COORD


class TestBuildRelativeReport:
    def test_report_length(self) -> None:
        report = build_relative_report()
        assert len(report) == 5

    def test_mode_byte(self) -> None:
        report = build_relative_report()
        assert report[0] == MOUSE_MODE_RELATIVE

    def test_zero_movement(self) -> None:
        report = build_relative_report()
        assert report == [MOUSE_MODE_RELATIVE, 0, 0, 0, 0]

    def test_positive_movement(self) -> None:
        report = build_relative_report(dx=10, dy=20)
        assert report[2] == 10
        assert report[3] == 20

    def test_negative_movement(self) -> None:
        report = build_relative_report(dx=-10, dy=-20)
        assert report[2] == (-10) & 0xFF
        assert report[3] == (-20) & 0xFF

    def test_clamp_max(self) -> None:
        report = build_relative_report(dx=200, dy=200)
        assert report[2] == 127
        assert report[3] == 127

    def test_clamp_min(self) -> None:
        report = build_relative_report(dx=-200, dy=-200)
        assert report[2] == (-127) & 0xFF
        assert report[3] == (-127) & 0xFF

    def test_buttons(self) -> None:
        report = build_relative_report(buttons=MouseButton.RIGHT)
        assert report[1] == MouseButton.RIGHT

    def test_wheel(self) -> None:
        report = build_relative_report(wheel=-3)
        assert report[4] == (-3) & 0xFF
