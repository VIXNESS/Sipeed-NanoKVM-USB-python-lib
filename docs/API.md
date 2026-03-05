# nanokvm API Reference

**Version:** 0.1.0
**License:** MIT
**Python:** >= 3.12

Python library for controlling machines via NanoKVM-USB — serial HID keyboard/mouse control + UVC video capture, designed for AI agent integration.

## Installation

```bash
pip install nanokvm
# or with uv
uv add nanokvm
```

**Dependencies:** `pyserial >= 3.5`, `opencv-python >= 4.8`, `numpy >= 1.26`

## Quick Start

```python
from nanokvm import NanoKVM

kvm = NanoKVM(serial_port="/dev/ttyACM0", video_device=0)
kvm.connect()

frame = kvm.capture_frame_base64()   # for LLM vision APIs
kvm.type_text("hello world")
kvm.press_key("Enter")
kvm.mouse_click(0.5, 0.5)

kvm.disconnect()
```

## Serial Port Paths by Platform

| Platform | Typical Path |
|----------|-------------|
| Linux | `/dev/ttyACM0` |
| macOS | `/dev/cu.usbmodemXXXX` or `/dev/cu.usbserial-XXXXX` |
| Windows | `COM3` |

Use `SerialConnection.list_ports()` to discover available ports.

---

## NanoKVM

`from nanokvm import NanoKVM`

The main high-level API. Combines serial (keyboard/mouse HID) and video capture into a single interface.

### Constructor

```python
NanoKVM(
    serial_port: str | None = None,
    baud_rate: int = 57600,
    video_device: int | str | None = None,
    video_width: int = 1920,
    video_height: int = 1080,
    video_fps: int = 30,
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `serial_port` | `str \| None` | `None` | Serial device path. |
| `baud_rate` | `int` | `57600` | Serial baud rate. |
| `video_device` | `int \| str \| None` | `None` | OpenCV camera index or device path. |
| `video_width` | `int` | `1920` | Requested capture width. |
| `video_height` | `int` | `1080` | Requested capture height. |
| `video_fps` | `int` | `30` | Requested frame rate. |

Supports context manager usage:

```python
with NanoKVM(serial_port="/dev/ttyACM0", video_device=0) as kvm:
    kvm.type_text("hello")
```

### Connection

#### `connect(serial_port=None, video_device=None) -> InfoPacket | None`

Open serial and/or video connections. Parameters override constructor values. Returns `InfoPacket` if serial is connected, `None` otherwise.

#### `disconnect() -> None`

Close all connections.

#### `is_connected: bool` (property)

`True` if the serial port is open.

#### `has_video: bool` (property)

`True` if the video device is open.

### Device Info

#### `get_info() -> InfoPacket`

Query device info including chip version, connection state, and keyboard lock LED status.

```python
info = kvm.get_info()
print(info.chip_version)   # e.g. "V1.4"
print(info.caps_lock)      # True / False
```

### Keyboard

#### `press_key(key: str, hold: float = 0.02) -> None`

Press and release a single key.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `key` | `str` | — | Key name (see [Key Names](#key-names)). |
| `hold` | `float` | `0.02` | Seconds to hold before releasing. |

```python
kvm.press_key("Enter")
kvm.press_key("F5")
kvm.press_key("win")       # Windows/Super key
```

#### `key_down(key: str) -> None`

Press a key without releasing it.

#### `key_up(key: str) -> None`

Release a previously pressed key.

#### `key_combo(keys: list[str], hold: float = 0.02) -> None`

Press a key combination and release. Keys are pressed in order and released in reverse order.

```python
kvm.key_combo(["ctrl", "c"])           # Copy
kvm.key_combo(["ctrl", "shift", "s"])  # Save As
kvm.key_combo(["alt", "F4"])           # Close window
kvm.key_combo(["win", "e"])            # Open Explorer
```

#### `release_all_keys() -> None`

Release all pressed keys and modifiers.

#### `type_text(text: str, delay: float = 0.05) -> None`

Type a string of ASCII characters one by one.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `text` | `str` | — | ASCII printable characters, `\t`, `\n`. |
| `delay` | `float` | `0.05` | Delay between keystrokes in seconds. |

```python
kvm.type_text("Hello, World!")
kvm.type_text("fast typing", delay=0.02)
```

Supported characters: letters, digits, symbols (`!@#$%^&*()_+-=[]{}|;':",.<>?/\``), tab (`\t`), newline (`\n` sends Enter).

### Mouse

All absolute positions use **normalized coordinates** where `(0.0, 0.0)` is the top-left and `(1.0, 1.0)` is the bottom-right.

#### `mouse_move(x: float, y: float) -> None`

Move the mouse to an absolute position (absolute HID mode).

| Parameter | Type | Description |
|-----------|------|-------------|
| `x` | `float` | Normalized X (0.0 = left, 1.0 = right). |
| `y` | `float` | Normalized Y (0.0 = top, 1.0 = bottom). |

> **Note:** Absolute mode may not work reliably at screen edges (0.0 / 1.0). Use `mouse_move_to()` for edge positions.

#### `mouse_move_to(x: float, y: float, screen_width: int = 1920, screen_height: int = 1080) -> None`

Move the mouse to a screen position using **relative mode**. Resets the cursor to the top-left corner first, then moves to the target pixel position. Use this when absolute mode fails at screen edges.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `x` | `float` | — | Normalized X (0.0 = left, 1.0 = right). |
| `y` | `float` | — | Normalized Y (0.0 = top, 1.0 = bottom). |
| `screen_width` | `int` | `1920` | Target screen width in pixels. |
| `screen_height` | `int` | `1080` | Target screen height in pixels. |

```python
kvm.mouse_move_to(0.0, 0.0)    # top-left corner
kvm.mouse_move_to(1.0, 1.0)    # bottom-right corner
kvm.mouse_move_to(0.5, 0.5)    # center
```

#### `mouse_click(x=None, y=None, button="left", hold=0.05) -> None`

Click a mouse button. If `x` and `y` are provided, clicks at that absolute position. If omitted, clicks in place using relative mode.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `x` | `float \| None` | `None` | Normalized X. `None` = click in place. |
| `y` | `float \| None` | `None` | Normalized Y. `None` = click in place. |
| `button` | `str \| int` | `"left"` | `"left"`, `"right"`, `"middle"`, `"back"`, `"forward"`, or bit value. |
| `hold` | `float` | `0.05` | Seconds to hold button down. |

```python
kvm.mouse_click()                          # left click in place
kvm.mouse_click(x=0.5, y=0.5)             # left click at center
kvm.mouse_click(x=0.7, y=0.3, button="right")  # right click
```

> **Tip:** After positioning with `mouse_move_to()`, use `mouse_click()` without coordinates to avoid mixing absolute/relative modes.

#### `mouse_double_click(x=None, y=None, button="left", interval=0.1) -> None`

Double-click at a position.

#### `mouse_move_relative(dx: int, dy: int, step_delay: float = 0.005) -> None`

Move the mouse by a relative pixel offset. Accepts any integer distance; large moves are automatically split into multiple HID reports.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dx` | `int` | — | Horizontal movement in pixels (any integer). |
| `dy` | `int` | — | Vertical movement in pixels (any integer). |
| `step_delay` | `float` | `0.005` | Seconds between chunked reports. |

```python
kvm.mouse_move_relative(100, 0)     # move 100px right
kvm.mouse_move_relative(-50, 200)   # move 50px left, 200px down
kvm.mouse_move_relative(2000, 0)    # large move, auto-chunked
```

#### `mouse_scroll(delta: int) -> None`

Scroll the mouse wheel.

| Parameter | Type | Description |
|-----------|------|-------------|
| `delta` | `int` | Scroll amount (-127 to 127). Negative = scroll down. |

```python
kvm.mouse_scroll(-3)   # scroll down
kvm.mouse_scroll(5)    # scroll up
```

#### `mouse_button_down(button="left") -> None`

Press a mouse button without releasing it.

#### `mouse_button_up(button="left") -> None`

Release a mouse button.

#### `mouse_reset() -> None`

Release all mouse buttons.

### Video Capture

#### `capture_frame() -> NDArray[np.uint8]`

Capture a single video frame as a BGR numpy array of shape `(height, width, 3)`.

```python
import cv2
frame = kvm.capture_frame()
cv2.imwrite("screenshot.png", frame)
```

#### `capture_frame_rgb() -> NDArray[np.uint8]`

Capture a frame in RGB color order.

#### `capture_frame_jpeg(quality: int = 85) -> bytes`

Capture a frame as raw JPEG bytes.

#### `capture_frame_base64(quality: int = 85) -> str`

Capture a frame as a base64-encoded JPEG string. Ready to send to multimodal LLM APIs (OpenAI, Anthropic, etc.).

```python
b64 = kvm.capture_frame_base64(quality=80)
```

#### `get_video_resolution() -> tuple[int, int]`

Return the current video capture resolution as `(width, height)`.

---

## VideoCapture

`from nanokvm import VideoCapture`

Low-level UVC video capture using OpenCV. The NanoKVM-USB exposes HDMI input as a standard USB camera.

### `open(device=0, width=1920, height=1080, fps=30) -> None`

Open a UVC video device.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `device` | `int \| str` | `0` | Device index or device path. |
| `width` | `int` | `1920` | Requested capture width. |
| `height` | `int` | `1080` | Requested capture height. |
| `fps` | `int` | `30` | Requested frame rate. |

### `close() -> None`

Release the video capture device.

### `read_frame() -> NDArray[np.uint8]`

Capture a single frame as a BGR numpy array of shape `(height, width, 3)`.

### `read_frame_rgb() -> NDArray[np.uint8]`

Capture a frame converted to RGB color order.

### `read_frame_jpeg(quality: int = 85) -> bytes`

Capture a frame as JPEG bytes.

### `read_frame_base64(quality: int = 85) -> str`

Capture a frame as a base64-encoded JPEG string.

### `get_resolution() -> tuple[int, int]`

Return current `(width, height)`.

### `get_fps() -> float`

Return current FPS.

### `list_devices(max_index: int = 10) -> list[dict]` (static)

Probe video device indices `0..max_index` and return info for each available device.

```python
from nanokvm import VideoCapture

for dev in VideoCapture.list_devices():
    print(f"Index {dev['index']}: {dev['width']}x{dev['height']} @ {dev['fps']} fps ({dev['backend']})")
```

Each dict contains: `index`, `width`, `height`, `fps`, `backend`.

### `is_open: bool` (property)

`True` if the capture device is open.

---

## KeyboardReport

`from nanokvm import KeyboardReport`

Low-level HID keyboard report builder. Produces standard 8-byte USB HID Boot Keyboard reports: `[modifier_bitmap, 0x00, key1, key2, key3, key4, key5, key6]`.

### `key_down(code: str) -> list[int]`

Register a key press and return the 8-byte HID report.

### `key_up(code: str) -> list[int]`

Register a key release and return the 8-byte HID report.

### `reset() -> list[int]`

Release all keys and modifiers. Returns an empty report.

### `char_to_report(ch: str) -> tuple[list[int], list[int]]`

Convert a single ASCII character to `(key_down_report, key_up_report)`.

---

## Key Names

Keys can be specified using either **event codes** or **friendly aliases** (case-insensitive).

### Friendly Aliases

| Alias | Maps To | Description |
|-------|---------|-------------|
| `"enter"`, `"return"` | `Enter` | Enter key |
| `"esc"`, `"escape"` | `Escape` | Escape key |
| `"backspace"`, `"bs"` | `Backspace` | Backspace |
| `"tab"` | `Tab` | Tab key |
| `"space"` | `Space` | Space bar |
| `"delete"`, `"del"` | `Delete` | Delete key |
| `"insert"`, `"ins"` | `Insert` | Insert key |
| `"home"` | `Home` | Home key |
| `"end"` | `End` | End key |
| `"pageup"`, `"pgup"` | `PageUp` | Page Up |
| `"pagedown"`, `"pgdn"` | `PageDown` | Page Down |
| `"up"` | `ArrowUp` | Arrow Up |
| `"down"` | `ArrowDown` | Arrow Down |
| `"left"` | `ArrowLeft` | Arrow Left |
| `"right"` | `ArrowRight` | Arrow Right |
| `"capslock"`, `"caps"` | `CapsLock` | Caps Lock |
| `"printscreen"`, `"prtsc"` | `PrintScreen` | Print Screen |
| `"menu"` | `ContextMenu` | Context Menu |
| `"f1"` .. `"f12"` | `F1` .. `F12` | Function keys |

Single characters are auto-resolved: `"a"` -> `KeyA`, `"1"` -> `Digit1`.

### Modifier Aliases

| Alias | Maps To | Description |
|-------|---------|-------------|
| `"ctrl"`, `"control"` | `ControlLeft` | Left Control |
| `"shift"` | `ShiftLeft` | Left Shift |
| `"alt"` | `AltLeft` | Left Alt |
| `"win"`, `"cmd"`, `"super"`, `"meta"` | `MetaLeft` | Windows / Command / Super key |
| `"rctrl"` | `ControlRight` | Right Control |
| `"rshift"` | `ShiftRight` | Right Shift |
| `"ralt"` | `AltRight` | Right Alt |
| `"rmeta"` | `MetaRight` | Right Meta |

### Modifier Bits

Byte 0 of the HID report:

| Key | Bit |
|-----|-----|
| `ControlLeft` | `0x01` |
| `ShiftLeft` | `0x02` |
| `AltLeft` | `0x04` |
| `MetaLeft` | `0x08` |
| `ControlRight` | `0x10` |
| `ShiftRight` | `0x20` |
| `AltRight` | `0x40` |
| `MetaRight` | `0x80` |

### All Event Codes

<details>
<summary>Full keycode table (click to expand)</summary>

| Event Code | HID Usage |
|------------|-----------|
| **Letters** | |
| `KeyA` .. `KeyZ` | `0x04` .. `0x1D` |
| **Digits** | |
| `Digit0` | `0x27` |
| `Digit1` .. `Digit9` | `0x1E` .. `0x26` |
| **Special** | |
| `Enter` | `0x28` |
| `Escape` | `0x29` |
| `Backspace` | `0x2A` |
| `Tab` | `0x2B` |
| `Space` | `0x2C` |
| `Minus` | `0x2D` |
| `Equal` | `0x2E` |
| `BracketLeft` | `0x2F` |
| `BracketRight` | `0x30` |
| `Backslash` | `0x31` |
| `Semicolon` | `0x33` |
| `Quote` | `0x34` |
| `Backquote` | `0x35` |
| `Comma` | `0x36` |
| `Period` | `0x37` |
| `Slash` | `0x38` |
| `CapsLock` | `0x39` |
| **Function Keys** | |
| `F1` .. `F12` | `0x3A` .. `0x45` |
| `F13` .. `F24` | `0x68` .. `0x73` |
| **Control Keys** | |
| `PrintScreen` | `0x46` |
| `ScrollLock` | `0x47` |
| `Pause` | `0x48` |
| `Insert` | `0x49` |
| `Home` | `0x4A` |
| `PageUp` | `0x4B` |
| `Delete` | `0x4C` |
| `End` | `0x4D` |
| `PageDown` | `0x4E` |
| **Arrow Keys** | |
| `ArrowRight` | `0x4F` |
| `ArrowLeft` | `0x50` |
| `ArrowDown` | `0x51` |
| `ArrowUp` | `0x52` |
| **Numpad** | |
| `NumLock` | `0x53` |
| `NumpadDivide` | `0x54` |
| `NumpadMultiply` | `0x55` |
| `NumpadSubtract` | `0x56` |
| `NumpadAdd` | `0x57` |
| `NumpadEnter` | `0x58` |
| `Numpad0` .. `Numpad9` | `0x62`, `0x59` .. `0x61` |
| `NumpadDecimal` | `0x63` |
| **Media** | |
| `AudioVolumeMute` | `0x7F` |
| `AudioVolumeUp` | `0x80` |
| `AudioVolumeDown` | `0x81` |
| `MediaPlayPause` | `0xE8` |
| `MediaStop` | `0xE9` |
| `MediaTrackPrevious` | `0xEA` |
| `MediaTrackNext` | `0xEB` |
| **Modifiers** | |
| `ControlLeft` | `0xE0` |
| `ShiftLeft` | `0xE1` |
| `AltLeft` | `0xE2` |
| `MetaLeft` / `WinLeft` | `0xE3` |
| `ControlRight` | `0xE4` |
| `ShiftRight` | `0xE5` |
| `AltRight` | `0xE6` |
| `MetaRight` / `WinRight` | `0xE7` |

</details>

---

## Mouse Module

`from nanokvm import MouseButton, build_absolute_report, build_relative_report`

### MouseButton

Button bit constants:

| Constant | Value | Description |
|----------|-------|-------------|
| `MouseButton.LEFT` | `0x01` | Left button |
| `MouseButton.RIGHT` | `0x02` | Right button |
| `MouseButton.MIDDLE` | `0x04` | Middle button |
| `MouseButton.BACK` | `0x08` | Back button |
| `MouseButton.FORWARD` | `0x10` | Forward button |

### `build_absolute_report(x, y, buttons=0, wheel=0) -> list[int]`

Build a 7-byte absolute mouse report: `[0x02, buttons, x_lo, x_hi, y_lo, y_hi, wheel]`.

| Parameter | Type | Description |
|-----------|------|-------------|
| `x` | `float` | Normalized X (0.0 to 1.0). |
| `y` | `float` | Normalized Y (0.0 to 1.0). |
| `buttons` | `int` | Button bitmap. |
| `wheel` | `int` | Scroll wheel (-127 to 127). |

Coordinates are mapped to a 12-bit range (0-4096).

### `build_relative_report(dx=0, dy=0, buttons=0, wheel=0) -> list[int]`

Build a 5-byte relative mouse report: `[0x01, buttons, dx, dy, wheel]`.

| Parameter | Type | Description |
|-----------|------|-------------|
| `dx` | `int` | X movement (-127 to 127). |
| `dy` | `int` | Y movement (-127 to 127). |
| `buttons` | `int` | Button bitmap. |
| `wheel` | `int` | Scroll wheel (-127 to 127). |

---

## Protocol

`from nanokvm import CmdEvent, CmdPacket, InfoPacket`

### CmdEvent

Serial command codes (IntEnum):

| Command | Value | Description |
|---------|-------|-------------|
| `GET_INFO` | `0x01` | Query device info |
| `SEND_KB_GENERAL_DATA` | `0x02` | Send keyboard HID report |
| `SEND_KB_MEDIA_DATA` | `0x03` | Send media key report |
| `SEND_MS_ABS_DATA` | `0x04` | Send absolute mouse report |
| `SEND_MS_REL_DATA` | `0x05` | Send relative mouse report |
| `SEND_MY_HID_DATA` | `0x06` | Send custom HID data |
| `READ_MY_HID_DATA` | `0x87` | Read custom HID data |
| `GET_PARA_CFG` | `0x08` | Get parameter config |
| `SET_PARA_CFG` | `0x09` | Set parameter config |
| `GET_USB_STRING` | `0x0A` | Get USB string descriptor |
| `SET_USB_STRING` | `0x0B` | Set USB string descriptor |
| `SET_DEFAULT_CFG` | `0x0C` | Restore default config |
| `RESET` | `0x0F` | Reset device |

### CmdPacket

Serial packet container. Packet format: `[0x57, 0xAB, ADDR, CMD, LEN, ...DATA, CHECKSUM]`.

#### `encode() -> bytes`

Serialize the packet to bytes for transmission.

#### `CmdPacket.decode(buf: bytes | list[int]) -> CmdPacket` (classmethod)

Parse a raw byte buffer into a `CmdPacket`. Validates header and checksum.

#### Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `addr` | `int` | `0x00` | Device address. |
| `cmd` | `int` | `0x00` | Command code (see `CmdEvent`). |
| `data` | `list[int]` | `[]` | Payload bytes. |

### InfoPacket

Device info returned by `GET_INFO`.

#### `InfoPacket.from_data(data: list[int]) -> InfoPacket` (classmethod)

Parse the `GET_INFO` response payload.

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| `chip_version` | `str` | Chip version string, e.g. `"V1.4"`. |
| `is_connected` | `bool` | Whether a USB host is connected. |
| `num_lock` | `bool` | Num Lock LED state. |
| `caps_lock` | `bool` | Caps Lock LED state. |
| `scroll_lock` | `bool` | Scroll Lock LED state. |

---

## SerialConnection

`from nanokvm import SerialConnection`

Low-level serial port wrapper using pyserial.

### `open(port: str, baud_rate: int = 57600) -> None`

Open a serial port. Closes any existing connection first.

### `close() -> None`

Close the serial port.

### `write(data: bytes) -> None`

Write bytes to the serial port and flush.

### `read(min_size: int, timeout: float = 0.5) -> list[int]`

Read at least `min_size` bytes from the serial port.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `min_size` | `int` | — | Minimum number of bytes to read. |
| `timeout` | `float` | `0.5` | Read timeout in seconds. |

### `list_ports() -> list[ListPortInfo]` (static)

List all available serial ports on the system.

```python
from nanokvm import SerialConnection

for port in SerialConnection.list_ports():
    print(f"{port.device}: {port.description}")
```

### `is_open: bool` (property)

`True` if the serial port is open.

---

## Module Structure

```
nanokvm/
├── __init__.py      # Public exports
├── device.py        # NanoKVM high-level API
├── keyboard.py      # HID keyboard reports and keymaps
├── mouse.py         # HID mouse report builders
├── protocol.py      # Serial packet format
├── serial_conn.py   # Serial port wrapper
└── video.py         # UVC video capture (OpenCV)
```
