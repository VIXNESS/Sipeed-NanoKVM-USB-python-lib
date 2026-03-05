"""
Basic NanoKVM usage: connect, check device info, type text, click, capture a frame.
"""

from nanokvm import NanoKVM

# 1. Create and connect
#    - serial_port: your NanoKVM serial device (Linux: /dev/ttyACM0, macOS: /dev/cu.usbmodemXXXX, Windows: COM3)
#    - video_device: OpenCV camera index for the NanoKVM UVC capture (often 0 or 1)
kvm = NanoKVM(serial_port="/dev/ttyACM0", video_device=0)
kvm.connect()

# 2. Check device info
info = kvm.get_info()
print(f"Chip: {info.chip_version}, Connected: {info.is_connected}")
print(f"CapsLock: {info.caps_lock}, NumLock: {info.num_lock}")

# 3. Type text
kvm.type_text("Hello from NanoKVM!")
kvm.press_key("Enter")

# 4. Key combo (Ctrl+A to select all)
kvm.key_combo(["ctrl", "a"])

# 5. Mouse - click at center of screen
kvm.mouse_click(x=0.5, y=0.5)

# 6. Mouse - right-click
kvm.mouse_click(x=0.7, y=0.3, button="right")

# 7. Mouse - scroll down
kvm.mouse_scroll(-3)

# 8. Capture a frame
frame_bgr = kvm.capture_frame()
print(f"Frame shape: {frame_bgr.shape}")  # e.g. (1080, 1920, 3)

# 9. Get a base64 JPEG (ready for LLM vision API)
b64 = kvm.capture_frame_base64(quality=80)
print(f"Base64 JPEG length: {len(b64)} chars")

# 10. Disconnect
kvm.disconnect()
