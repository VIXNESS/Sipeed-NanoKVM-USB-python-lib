# nanokvm

Python library for controlling machines via [NanoKVM-USB](https://sipeed.com/nanokvm/usb) — serial HID keyboard/mouse control + UVC video capture, designed for AI agent integration.

## Architecture

```
Python Agent                NanoKVM-USB              Target Machine
┌──────────┐  serial/HID   ┌───────────┐  USB HID   ┌──────────────┐
│ nanokvm  │──────────────>│           │────────────>│  keyboard    │
│ library  │               │  NanoKVM   │            │  mouse       │
│          │  UVC video    │  USB       │  HDMI in   │              │
│          │<──────────────│           │<────────────│  display     │
└──────────┘               └───────────┘             └──────────────┘
```

The NanoKVM-USB exposes two USB interfaces to the host:
- **USB Serial** (57600 baud) — sends keyboard and mouse HID reports
- **USB Video (UVC)** — receives HDMI video as a standard camera device

## Install

Install directly from GitHub:

```bash
pip install git+https://github.com/Sipeed/NanoKVM-USB-python-lib.git
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv pip install git+https://github.com/Sipeed/NanoKVM-USB-python-lib.git
```

To add as a dependency to an existing uv project:

```bash
uv add nanokvm --git https://github.com/Sipeed/NanoKVM-USB-python-lib.git
```

Or pin to a specific version tag:

```bash
uv add nanokvm --git https://github.com/Sipeed/NanoKVM-USB-python-lib.git --tag v0.1.1
```

For local development:

```bash
git clone https://github.com/Sipeed/NanoKVM-USB-python-lib.git
cd NanoKVM-USB-python-lib
uv pip install -e ".[dev]"
```

## Quick Start

```python
from nanokvm import NanoKVM

kvm = NanoKVM(
    serial_port="/dev/ttyACM0",  # Linux. macOS: /dev/cu.usbmodemXXXX, Windows: COM3
    video_device=0,               # OpenCV camera index
)
kvm.connect()

# Check device
info = kvm.get_info()
print(f"Version: {info.chip_version}, Connected: {info.is_connected}")

# Capture screen (for AI vision)
b64_jpeg = kvm.capture_frame_base64()  # ready for GPT-4o, Claude, etc.
frame = kvm.capture_frame()            # numpy array (H, W, 3) BGR

# Keyboard
kvm.type_text("hello world")
kvm.press_key("Enter")
kvm.key_combo(["ctrl", "c"])           # Ctrl+C

# Mouse (absolute, normalized 0-1 coordinates)
kvm.mouse_move(0.5, 0.5)              # move to center
kvm.mouse_click(0.5, 0.5)             # left click at center
kvm.mouse_click(0.7, 0.3, button="right")
kvm.mouse_scroll(-3)                   # scroll down

kvm.disconnect()
```

## API Reference

### `NanoKVM(serial_port, video_device, ...)`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `serial_port` | `str \| None` | `None` | Serial port path |
| `baud_rate` | `int` | `57600` | Serial baud rate |
| `video_device` | `int \| str \| None` | `None` | OpenCV device index or path |
| `video_width` | `int` | `1920` | Requested video width |
| `video_height` | `int` | `1080` | Requested video height |
| `video_fps` | `int` | `30` | Requested frame rate |

### Connection

| Method | Description |
|--------|-------------|
| `connect()` | Open serial and video connections |
| `disconnect()` | Close all connections |
| `get_info()` | Query device version, connected state, lock LEDs |

### Keyboard

| Method | Description |
|--------|-------------|
| `press_key(key)` | Press and release a key |
| `key_combo(keys)` | Press a combination (e.g. `["ctrl", "c"]`) |
| `type_text(text)` | Type ASCII string character by character |
| `key_down(key)` / `key_up(key)` | Low-level press/release |
| `release_all_keys()` | Release everything |

Key names accept both `event.code` format (`"KeyA"`, `"Enter"`) and friendly names (`"a"`, `"enter"`, `"ctrl"`, `"f1"`).

### Mouse

| Method | Description |
|--------|-------------|
| `mouse_move(x, y)` | Move to absolute position (0.0-1.0) |
| `mouse_click(x, y, button)` | Click at position |
| `mouse_double_click(x, y)` | Double-click |
| `mouse_move_relative(dx, dy)` | Relative movement (-127..127) |
| `mouse_scroll(delta)` | Scroll wheel |
| `mouse_button_down(button)` / `mouse_button_up(button)` | Low-level |

### Video

| Method | Description |
|--------|-------------|
| `capture_frame()` | BGR numpy array |
| `capture_frame_rgb()` | RGB numpy array |
| `capture_frame_jpeg(quality)` | JPEG bytes |
| `capture_frame_base64(quality)` | Base64 JPEG string (for LLM APIs) |
| `get_video_resolution()` | Current (width, height) |

### Utilities

```python
from nanokvm import SerialConnection, VideoCapture

# List available serial ports
for port in SerialConnection.list_ports():
    print(f"{port.device}: {port.description}")

# List available video devices
for dev in VideoCapture.list_devices():
    print(f"Index {dev['index']}: {dev['width']}x{dev['height']} @ {dev['fps']}fps")
```

## Documentation

For the full API reference covering all classes, methods, parameters, key maps, and HID protocol details, see [docs/API.md](docs/API.md).

## AI Agent Example

See [`examples/ai_agent_loop.py`](examples/ai_agent_loop.py) for a complete observe-act loop pattern.

## Platform Notes

- **Linux**: Add your user to the `dialout` group for serial access: `sudo usermod -aG dialout $USER`
- **macOS**: Serial port is typically `/dev/cu.usbmodemXXXX`
- **Windows**: Serial port is `COM3` or similar (check Device Manager)

## License

[MIT](LICENSE)
