# NanoKVM Constitution

## Core Principles

### I. Library-First
Every feature starts as a standalone module within the nanokvm package; Modules must be self-contained, independently testable, and documented; Clear purpose required - no organizational-only modules.

### II. Type Safety (NON-NEGOTIABLE)
All code MUST use Python 3.10+ type hints; pyright type checking must pass; Forward references enabled via `from __future__ import annotations`.

### III. Test-First (NON-NEGOTIABLE)
Tests written before implementation; pytest for all tests; Test file naming: test_<module>.py; Place tests in tests/ directory.

### IV. Code Quality Standards
ruff for formatting and linting; Google-style docstrings with Args:/Returns: sections; Use dataclasses for simple data containers; Use IntEnum for related constants.

### V. Observability & Debuggability
Text I/O ensures debuggability; Descriptive error messages with context; Clear __repr__ for debugging.

## Technology Stack

Python 3.12+ required; Primary dependencies: pyserial, opencv-python, numpy; Testing framework: pytest; Type checking: pyright; Code formatting: ruff.

## Development Workflow

Pre-commit checklist: ruff format, ruff check, pyright, pytest; Use context managers for resource safety; Ensure clean disconnect() methods; Follow naming conventions: PascalCase classes, snake_case functions, UPPER_SNAKE_CASE constants.

## Governance

Constitution supersedes all other practices; Amendments require documentation, approval, and migration plan; All PRs/reviews must verify compliance; Use AGENTS.md for runtime development guidance.

**Version**: 1.0.0 | **Ratified**: 2026-03-06 | **Last Amended**: 2026-03-06
