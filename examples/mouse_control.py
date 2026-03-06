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
    python examples/mouse_control.py --port /dev/ttyACM0 --video 0 --record
    python examples/mouse_control.py --port /dev/ttyACM0 --video 0 --record --output my_recording.mp4
"""

from __future__ import annotations

import argparse
import threading
import time
from datetime import datetime

import cv2

from nanokvm import NanoKVM

PAUSE = 0.8


class ScreenRecorder:
    """Records KVM screen output to a video file in a background thread."""

    def __init__(self, kvm: NanoKVM, output_path: str, fps: float = 10) -> None:
        self._kvm = kvm
        self._output_path = output_path
        self._fps = fps
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._frame_count = 0

    @property
    def frame_count(self) -> int:
        return self._frame_count

    def start(self) -> None:
        self._stop.clear()
        self._frame_count = 0
        self._thread = threading.Thread(target=self._record_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=5)

    def _record_loop(self) -> None:
        writer: cv2.VideoWriter | None = None
        interval = 1.0 / self._fps

        try:
            while not self._stop.is_set():
                t0 = time.monotonic()
                try:
                    frame = self._kvm.capture_frame()
                except Exception:
                    self._stop.wait(interval)
                    continue

                if writer is None:
                    h, w = frame.shape[:2]
                    fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # type: ignore[reportAttributeAccessIssue]
                    writer = cv2.VideoWriter(
                        self._output_path, fourcc, self._fps, (w, h)
                    )
                    if not writer.isOpened():
                        print(
                            f"  [recorder] Failed to open VideoWriter for {self._output_path}"
                        )
                        return

                writer.write(frame)
                self._frame_count += 1

                elapsed = time.monotonic() - t0
                remaining = interval - elapsed
                if remaining > 0:
                    self._stop.wait(remaining)
        finally:
            if writer is not None:
                writer.release()

    def __enter__(self) -> ScreenRecorder:
        self.start()
        return self

    def __exit__(self, *_: object) -> None:
        self.stop()


def test_absolute_mode(kvm: NanoKVM) -> None:
    """Move the cursor to several positions using absolute mode."""
    print("\n=== Absolute Mode ===")
    print("Moving cursor to five positions (corners + center)...\n")

    positions = [
        ("top-left", 0.05, 0.05),
        ("top-right", 0.95, 0.05),
        ("bottom-right", 0.95, 0.95),
        ("bottom-left", 0.05, 0.95),
        ("center", 0.50, 0.50),
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
        ("top-left", 0.0, 0.0),
        ("top-right", 1.0, 0.0),
        ("bottom-right", 1.0, 1.0),
        ("bottom-left", 0.0, 1.0),
        ("center", 0.5, 0.5),
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
    parser.add_argument(
        "--video", type=int, default=None, help="Video device index (optional)"
    )
    parser.add_argument(
        "--record", action="store_true", help="Record the KVM screen during tests"
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output video file path (default: recording_<timestamp>.mp4)",
    )
    parser.add_argument(
        "--record-fps",
        type=float,
        default=10,
        help="Recording frame rate (default: 10)",
    )
    args = parser.parse_args()

    if args.record and args.video is None:
        parser.error("--record requires --video to be set")

    if args.record and args.output is None:
        args.output = f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"

    kvm = NanoKVM(serial_port=args.port, video_device=args.video)
    kvm.connect()
    print(f"Connected: {kvm}")

    recorder: ScreenRecorder | None = None
    try:
        if args.record:
            recorder = ScreenRecorder(kvm, args.output, fps=args.record_fps)
            recorder.start()
            print(f"Recording started -> {args.output}")

        test_absolute_mode(kvm)
        test_relative_mode(kvm)
        test_relative_move_to(kvm)
        test_scroll(kvm)
        print("All mouse tests completed.")
    finally:
        if recorder is not None:
            recorder.stop()
            print(f"Recording saved: {args.output} ({recorder.frame_count} frames)")
        kvm.mouse_reset()
        kvm.disconnect()
        print("Disconnected.")


if __name__ == "__main__":
    main()
