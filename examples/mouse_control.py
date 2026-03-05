"""
Test NanoKVM mouse control in both Absolute and Relative modes.

Absolute mode:
  - Uses normalized coordinates (0.0–1.0) mapped to the full screen.
  - Jumps the cursor directly to the target position.

Relative mode:
  - Moves the cursor by a pixel offset from its current position.
  - Large offsets are automatically chunked into -127/+127 HID reports.
  - `mouse_move_to` resets to (0,0) then moves to the target position.

Usage:
    python examples/mouse_control.py --port /dev/ttyACM0
"""

import argparse
import time

from nanokvm import NanoKVM

PAUSE = 0.8


def test_absolute_mode(kvm: NanoKVM) -> None:
    """Move the cursor to several positions using absolute mode."""
    print("\n=== Absolute Mode ===")
    print("Moving cursor to five positions (corners + center)...\n")

    positions = [
        ("top-left",     0.05, 0.05),
        ("top-right",    0.95, 0.05),
        ("bottom-right", 0.95, 0.95),
        ("bottom-left",  0.05, 0.95),
        ("center",       0.50, 0.50),
    ]

    for name, x, y in positions:
        print(f"  mouse_move({x}, {y})  ->  {name}")
        kvm.mouse_move(x, y)
        time.sleep(PAUSE)

    print("\nAbsolute mode: draw a diagonal from top-left to bottom-right")
    steps = 20
    for i in range(steps + 1):
        t = i / steps
        kvm.mouse_move(0.1 + t * 0.8, 0.1 + t * 0.8)
        time.sleep(0.05)

    print("  Done.\n")


def test_relative_mode(kvm: NanoKVM) -> None:
    """Move the cursor using relative offsets."""
    print("\n=== Relative Mode ===")

    print("Resetting cursor to center via mouse_move (absolute)...")
    kvm.mouse_move(0.5, 0.5)
    time.sleep(PAUSE)

    movements = [
        ("right +200px", 200, 0),
        ("down  +150px", 0, 150),
        ("left  -200px", -200, 0),
        ("up    -150px", 0, -150),
    ]

    print("Drawing a rectangle with relative moves:\n")
    for label, dx, dy in movements:
        print(f"  mouse_move_relative(dx={dx:+d}, dy={dy:+d})  ->  {label}")
        kvm.mouse_move_relative(dx, dy)
        time.sleep(PAUSE)

    print("\nLarge relative move (dx=+500, dy=+300) — auto-chunked:")
    kvm.mouse_move_relative(500, 300)
    time.sleep(PAUSE)
    print("  Done.\n")


def test_relative_move_to(kvm: NanoKVM) -> None:
    """Use mouse_move_to (relative-based positioning) to visit corners."""
    print("\n=== Relative Mode — mouse_move_to ===")
    print("Visits corners using reset-to-origin + relative movement.\n")

    positions = [
        ("top-left",     0.0, 0.0),
        ("top-right",    1.0, 0.0),
        ("bottom-right", 1.0, 1.0),
        ("bottom-left",  0.0, 1.0),
        ("center",       0.5, 0.5),
    ]

    for name, x, y in positions:
        print(f"  mouse_move_to({x}, {y})  ->  {name}")
        kvm.mouse_move_to(x, y)
        time.sleep(PAUSE)

    print("  Done.\n")


def test_scroll(kvm: NanoKVM) -> None:
    """Scroll up and down at the center of the screen."""
    print("\n=== Scroll Test ===")
    kvm.mouse_move(0.5, 0.5)
    time.sleep(PAUSE)

    print("  Scrolling down (5 ticks)...")
    for _ in range(5):
        kvm.mouse_scroll(-3)
        time.sleep(0.15)

    time.sleep(PAUSE)

    print("  Scrolling up (5 ticks)...")
    for _ in range(5):
        kvm.mouse_scroll(3)
        time.sleep(0.15)

    print("  Done.\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="NanoKVM mouse control test")
    parser.add_argument("--port", default="/dev/ttyACM0", help="Serial port")
    parser.add_argument("--video", type=int, default=None, help="Video device index (optional)")
    args = parser.parse_args()

    kvm = NanoKVM(serial_port=args.port, video_device=args.video)
    kvm.connect()
    print(f"Connected: {kvm}")

    try:
        test_absolute_mode(kvm)
        test_relative_mode(kvm)
        test_relative_move_to(kvm)
        test_scroll(kvm)
        print("All mouse tests completed.")
    finally:
        kvm.mouse_reset()
        kvm.disconnect()
        print("Disconnected.")


if __name__ == "__main__":
    main()
