# AGENTS.md - Agent Coding Guidelines

This document provides guidelines for AI agents working in this repository.

## Project Overview

Python library for controlling machines via NanoKVM-USB — serial HID keyboard/mouse control + UVC video capture, designed for AI agent integration.

## Requirements

- Python 3.12+
- uv (recommended) or pip

## Development Setup

```bash
# Clone and install with dev dependencies
git clone https://github.com/Sipeed/NanoKVM-USB-python-lib.git
cd NanoKVM-USB-python-lib
uv pip install -e ".[dev]"
```

## Build/Lint/Test Commands

| Command | Description |
|---------|-------------|
| `uv pip install -e ".[dev]"` | Install package in editable mode with dev dependencies |
| `ruff check .` | Run linting with ruff |
| `ruff format .` | Format code with ruff |
| `pyright` | Run type checking with pyright |
| `pytest` | Run all tests |
| `pytest -xvs <test_file.py>` | Run a specific test file with verbose output |
| `pytest -xvs <test_file.py>::<TestClass>::<test_method>` | Run a specific test method |

### Example: Running a Single Test

```bash
# Run a specific test file
pytest -xvs tests/test_keyboard.py

# Run a specific test function
pytest -xvs tests/test_keyboard.py::test_resolve_key_code
```

## Code Style Guidelines

### General

- **Python version**: 3.12+ (uses modern syntax like `| None` unions)
- **Type checking**: Enabled (pyright basic mode)
- **Formatting**: ruff (line length follows default)

### Imports

Organize imports in the following order with blank lines between groups:

1. Standard library (`from __future__ import annotations`, `import time`, etc.)
2. Third-party packages (`numpy`, `opencv-python`, `pyserial`)
3. Local modules (`.module`)

```python
from __future__ import annotations

import time

import numpy as np
from numpy.typing import NDArray

from .keyboard import KeyboardReport
from .protocol import CmdEvent
```

### Type Hints

- Use Python 3.10+ union syntax: `str | None`, `int | str`
- Use `NDArray[np.uint8]` for numpy arrays
- Enable forward references with `from __future__ import annotations`

```python
def mouse_click(
    self,
    x: float | None = None,
    y: float | None = None,
    button: str | int = "left",
) -> None:
    ...
```

### Naming Conventions

- **Classes**: `PascalCase` (e.g., `NanoKVM`, `KeyboardReport`)
- **Functions/methods**: `snake_case` (e.g., `mouse_move`, `capture_frame`)
- **Private methods**: Prefix with `_` (e.g., `_send_keyboard`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `INTER_KEY_DELAY`, `HEAD1`)
- **Module-private**: Prefix with `_` (e.g., `_KEY_ALIASES`)

### Docstrings

Use Google-style docstrings with `Args:` and `Returns:` sections:

```python
def press_key(self, key: str, hold: float = KEY_HOLD_DELAY) -> None:
    """
    Press and release a single key.

    Args:
        key: Key name -- can be event.code ("KeyA", "Enter") or a friendly
             name ("a", "enter", "f1", "ctrl", "shift").
        hold: Seconds to hold the key before releasing.
    """
```

### Classes

- Use dataclasses for simple data containers with `@dataclass`
- Use enums for related constants with `IntEnum` when values are integers
- Implement `__repr__` for debugging

```python
from dataclasses import dataclass, field
from enum import IntEnum

class CmdEvent(IntEnum):
    GET_INFO = 0x01
    SEND_KB_GENERAL_DATA = 0x02

@dataclass
class CmdPacket:
    addr: int = 0x00
    cmd: int = 0x00
    data: list[int] = field(default_factory=list)
```

### Error Handling

- Use specific exception types (`ValueError`, `IOError`, etc.)
- Include descriptive error messages with context

```python
if remaining < 6:
    raise ValueError(f"Packet too short: {remaining} bytes after header")
```

### File Organization

```
nanokvm/
  __init__.py      # Public API exports
  __main__.py      # CLI entry point
  device.py        # NanoKVM main class
  keyboard.py      # Keyboard HID report builder
  mouse.py         # Mouse HID report builder
  protocol.py      # Serial protocol (packets, commands)
  serial_conn.py   # Serial connection handling
  video.py         # Video capture (OpenCV/UVC)
```

### Testing

- Place tests in `tests/` directory
- Use `pytest` with descriptive test names
- Test file naming: `test_<module>.py`

### Exception Safety

- Use context managers when possible (`with kvm.connect():`)
- Ensure resources are cleaned up in `disconnect()` methods

### Constants

Define module-level constants at the top of files after imports:

```python
from .keyboard import ...

INTER_KEY_DELAY = 0.05
KEY_HOLD_DELAY = 0.02
```

## Common Tasks

### Adding a New Method to NanoKVM

1. Add method to `nanokvm/device.py`
2. Use proper type hints and docstrings
3. Run `ruff format .` and `pyright`
4. Export in `nanokvm/__init__.py` if public API

### Adding Key Mappings

1. Add to `KEYCODE_MAP` in `nanokvm/keyboard.py`
2. Optionally add friendly alias to `_KEY_ALIASES`

## Pre-commit Checklist

Before committing:

- [ ] `ruff format .` (code formatting)
- [ ] `ruff check .` (linting)
- [ ] `pyright` (type checking)
- [ ] `pytest` (tests pass)
