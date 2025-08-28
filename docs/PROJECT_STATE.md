# Project State – DiceRealms (Python)

_Last updated: 2025-08-28_

## Overview
DiceRealms is a multiplayer MUD-style game inspired by D&D.  
Current focus: **[Milestone M1]**

> **Naming note:** The Python package directory is **`dicerealms/`** (no underscore).  
> Repository root is **`dicerealms-python/`**.

---

## Folder Structure
```bash
dicerealms-python/
├── dicerealms/             # Main package source
│   ├── __init__.py
│   ├── __main__.py         # Current Entry point for the game.
│   ├── cli.py              # CLI Entry point for the game.
│   ├── console_frontend.py # A simple console frontend.
│   ├── core.py             # Core game logic (dice rolling, realms, etc.)
│   ├── player.py           # Player, character, inventory
│   ├── world.py            # World/realm definitions
│   ├── engine.py           # Game loop, orchestrator
│   └── session.py          # A single player's session
│
├── examples/               # Example scripts
│   └── quickstart.py
│
├── tests/                  # Unit tests
│   ├── __init__.py
│   ├── test_core.py
│   └── test_engine.py
│
├── docs/                   # Various documents
│   ├── milestones
│   │   ├── M1.md
│   │   ├── M2.md
│   │   ├── M3.md
│   │   ├── M4.md
│   │   ├── M5.md
│   │   └── M6.md
│   ├── PROJECT_STATE.md    # This file
│   └── ...
│
├── ROADMAP.md              # Long-term roadmap
├── ...                     # ...
├── ...                     # ...
├── LICENSE
├── README.md
├── MILESTONES.md           # Break down of Milestones (Linked to M1-M6)
├── pyproject.toml
└── .gitignore
```

---

## Modules & Responsibilities

### dicerealms/cli.py
- **Purpose:** CLI Entry Point with Commands
- **Functions:**
  - `new()` – Starts a New Game.
  - `start()` – Starts the Game Engine.
  - `hello(name: str)` – Generic entry point.
  - `roll(expr: str)` – Do a dice roll.
- **Notes:** 

### dicerealms/core.py
- **Purpose:** Core mechanics (dice rolls, randomization utilities).
- **Functions:**
  - `roll_dice(dice: str) -> tuple[int, list[int]]` – roll dice uses regex to parse dice type and quantity.
- **Notes:** Utility functions, stateless.

### dicerealms/console_frontend.py
- **Purpose:** A simple console frontend that:
    - renders output with a write(str) callback
    - reads input lines in a background task
    - forwards lines to the GameSession
- **Classes:**
  - `ConsoleFrontend`
    - `__init__()`
    - `_write(text: str)`
    - `async start()`
    - `async _stdin_reader()`
    - `async def run()`
- **Notes:** I don't like the current naming convention for this file/class. Maybe it needs to be changed to console.py??.

### dicerealms/player.py
- **Purpose:** Player representation, stats, and inventory.
- **Classes:**
  - `Player`: dataclass
    - `name: str = "Adventurer"`
    - `room: str = "Town Square"`
- **Notes:** Player data is central, persisted later in M4.

### dicerealms/world.py
- **Purpose:** Defines rooms and realms, navigation logic.
- **Classes:**
  - Nothing Yet
- **Notes:** Placeholder world now, will expand in M2 & M4.

### dicerealms/engine.py
- **Purpose:** Orchestrates basic command handling. A minimal, synchronous REPL-like game engine.
- **Classes:**
  - `Command`: dataclass
    - `name: str`
    - `help: str`
    - `handler: Callable[[list[str]], str]`
  - `GameEngine`
    - `__init__(input_fn: Callable[[], str] | None, output_fn: Callable[[str], None] | None)`
    - `run()`
    - `_cmd_help(self, _: list[str]) -> str`
    - `_cmd_roll(self, args: list[str]) -> str`
    - `_cmd_look(self, _: list[str]) -> str`
    - `_cmd_quit(self, _: list[str]) -> str`
- **Notes:** Will eventually split into networking vs CLI engines.

### dicerealms/session.py
- **Purpose:** Orchestrates the game loop.
  - A single player's session: reads commands from an input queue, passess them
    to the Engine, and writes responses via a callback.
- **Classes:**
  - `GameSession`
    - `__init__(write_callback)`
    - `async start()`
    - `async _run()`
    - `async feed_line(line: str)`
    - `async wait_closed()`
- **Notes:** Not sure where this is going yet.

### dicerealms/__init__.py
- **Purpose:** Package exports, version.
- **Notes:** Placeholder.

### dicerealms/__main__.py
- **Purpose:** CLI entrypoint hook???
- **Functions:**
  - `async main()` – starts the 'run' command in ConsoleFrontend.
- **Notes:** Thin wrapper.

---

## Testing
- `tests/test_core.py` → covers dice rolling.
- `tests/test_engine.py` → covers base engine functionality.
- Future: add `tests/test_player.py`, `tests/test_world.py`.

---

## CLI / Interaction
- Framework: **Typer**
- Command entrypoint: `python -m dicerealms`
- Current commands:
  - `help`, `roll <expr>`, `look`, `quit`
- Planned/Upcoming commands:
  - `server` → run server for multiplayer
  - `connect` → connect via WebSocket
  - `start` → alias for `play` (TBD)

---

## Networking
_Current state: Not implemented_  
Planned options: WebSocket (primary), Telnet (optional).

---

## Milestones
- **M1:** ✅ Basic single-player loop with dice rolling + room navigation  
- **M2:** 🚀 Expand gameplay basics (navigation, actions, and command parser)  
- **M3:** Persistence (saving characters/world state)  
- **M4:** Advanced features (combat, NPCs, items, etc.)

---

## Notes & Conventions
- License: MIT (with possible future Apache-2.0 switch)  
- Code style: `ruff` for linting  
- Tests: `pytest`  

---

## Recent Changes
_A running log to avoid confusion between sessions. Add newest entries at the top._

- **2025-08-28** — Concluded `M1`. Added functional CLI, dice rolling, player/world placeholders, engine loop, and tests. Updated `README` with Quickstart. Logged changes in `CHANGES.md`. Moved project focus to `M2` (navigation, actions, parser expansion).
  _Author:_ Eric Harris

- **2025-08-28** — Created `PROJECT_STATE.md` with sections for structure, modules, CLI, networking, milestones, and conventions; added **Recent Changes** section. Made sure all file structure was currently active and the **Modules & Responsibilities** section has an accurate break down of what each file does currently, with method/function signatures.  
  _Author:_ Eric Harris

**How to update this section quickly**
1. Run a short tree dump when structure changes:
   ```bash
   tree -L 2 dicerealms/
   ```
2. Paste only the changed lines (or file additions) below the date.
3. If behavior changed (e.g., new CLI command), add a one-liner.

---

## Open Questions
- Do we support both CLI and WebSocket from the start?  
- Do we need persistence in M1 or wait until M3?  

---

## Refresh Cheatsheet (for quick context in chat)
- Paste this one-liner to recap focus:
  ```
  Current focus: M2 — expand gameplay basics (navigation, actions, parser); package dir: dicerealms; CLI: python -m dicerealms
  ```
- Paste a short tree dump when structure matters:
  ```
  tree -L 2 dicerealms/
  ```
