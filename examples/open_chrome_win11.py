"""
Record a NanoKVM session: open Chrome on Win11 and move the mouse to each corner.

Steps:
  1. Start background screen recording
  2. Press Win key, type "chrome", press Enter to launch Chrome
  3. Move the mouse: top-left -> top-right -> bottom-right -> bottom-left -> center
  4. Stop recording and save to recording.mp4
"""

import threading
import time

import cv2

from nanokvm import NanoKVM

kvm = NanoKVM(serial_port="/dev/cu.usbserial-31340", video_device=0)
kvm.connect()

# --- Screen recording setup ---
width, height = kvm.get_video_resolution()
fps = 30
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
writer = cv2.VideoWriter("recording.mp4", fourcc, fps, (width, height))
stop_event = threading.Event()


def record_loop() -> None:
    while not stop_event.is_set():
        try:
            frame = kvm.capture_frame()
            writer.write(frame)
        except Exception:
            pass
        time.sleep(1 / fps)


recorder = threading.Thread(target=record_loop, daemon=True)
recorder.start()
print("Recording started...")

# --- Open Chrome via Start menu ---
kvm.press_key("win")
time.sleep(1.5)

kvm.type_text("chrome")
time.sleep(1.0)

kvm.press_key("Enter")
time.sleep(3.0)

# --- Move mouse to each corner and center ---
positions = [
    ("top-left",     0.0, 0.0),
    ("top-right",    1.0, 0.0),
    ("bottom-right", 1.0, 1.0),
    ("bottom-left",  0.0, 1.0),
    ("center",       0.5, 0.5),
]

for name, x, y in positions:
    print(f"Moving mouse to {name} ({x}, {y})")
    kvm.mouse_move(x, y)
    time.sleep(1.0)

# --- Left click at center ---
kvm.mouse_click(x=0.5, y=0.5)
time.sleep(1.0)

# --- Stop recording and save ---
stop_event.set()
recorder.join()
writer.release()
print("Recording saved to recording.mp4")

kvm.disconnect()
