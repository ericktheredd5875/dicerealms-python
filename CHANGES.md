# Changelog – DiceRealms (Python)

This file tracks significant changes, additions, and fixes across the project.  
For high-level project state and structure, see `PROJECT_STATE.md`.

---

## Format
- Use reverse chronological order (newest entries first).
- Group by date, then list changes as bullet points.
- Keep entries concise (1–3 lines).

---

## [2025-08-28] — Milestone 1 Complete 🎉
- Finished package scaffolding (`dicerealms/`, tests, examples).
- Implemented core dice rolling system (`core.py`).
- Added player structure placeholder (`player.py`).
- Added world placeholder (`world.py`).
- Added basic game loop in `engine.py` with commands: `help`, `roll`, `look`, `quit`.
- Functional CLI via `python -m dicerealms` and `dicerealms` script.
- Added pytest unit tests for core functions.
- Updated README with Quickstart instructions.
- Created `examples/quickstart.py`.

_This concludes M1. Next: M2 — navigation, actions, and command parser._

---

## 2025-08-28
- **Added:** `PROJECT_STATE.md` with sections for structure, modules, CLI, networking, milestones, conventions, and recent changes.
- **Setup:** Created `CHANGES.md` template for tracking future updates.

---

## Template for future entries
### YYYY-MM-DD
- **Added:** ...
- **Changed:** ...
- **Fixed:** ...
- **Removed:** ...
