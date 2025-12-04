# 🎲 DiceRealms (Python)

**DiceRealms** is a modern, **multiplayer, turn-based** MUD-style roleplaying platform with beautiful terminal UIs. Built for immersive text-based storytelling, synchronized group adventures, and D&D-style dice mechanics.

Players connect via WebSocket to a shared game server, where actions are announced to all players, executed with synchronized animations, and results are broadcast simultaneously. Each player enjoys a rich terminal experience powered by **Rich** (output) and **prompt-toolkit** (input).

This project is in active development. Current milestone: **M2 — Gameplay Basics**.

---

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python](https://img.shields.io/badge/python-3.13%2B-blue)
![Status: In Development](https://img.shields.io/badge/status-alpha-orange)
[![codecov](https://codecov.io/gh/ericktheredd5875/dicerealms-python/graph/badge.svg?token=579MCVZ7P3)](https://codecov.io/gh/ericktheredd5875/dicerealms-python)

---

## ✨ Features

### Current (M1 Complete)
* 🎲 **Dice Rolling**: Support for expressions like `2d6+1`, with detailed roll breakdowns
* 👤 **Player System**: Character creation and basic player representation
* 🗺️ **World Foundation**: Room-based world structure (expanding in M2)
* 🎮 **CLI Interface**: Functional command-line interface with Typer

### Coming Soon (M2-M3)
* 🎨 **Rich Terminal UI**: Beautiful tables, panels, colors, and animations using Rich
* ⌨️ **Advanced Input**: Command history, autocomplete, and multi-line editing with prompt-toolkit
* 🌐 **Multiplayer Support**: WebSocket-based client-server architecture
* ⏱️ **Turn-Based Gameplay**: Synchronized actions where all players see announcements, wait together, and view results simultaneously
* 💬 **Real-Time Chat**: Say, whisper, and system messages
* 🎯 **Synchronized Actions**: When one player acts, everyone sees it happen in real-time

### Future (M4+)
* ⚔️ **Combat System**: Dice-based turn-based combat
* 🎒 **Items & Loot**: Rarity-based item generation
* 💾 **Persistence**: Save/load player state
* 🤖 **NPCs & Quests**: AI-driven interactions
* 🛠️ **GM Tools**: Admin commands and game management

---

## 🚀 Getting Started

### Prerequisites

* Python 3.13+
* [uv](https://github.com/astral-sh/uv) (recommended) or pip
* Git

### Installation

# Clone the repository
git clone https://github.com/ericktheredd5875/dicerealms-python.git
cd dicerealms-python

# Create virtual environment and install
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .

# Or with pip
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .### Quick Start (Single-Player)
```

# Run the game
```python -m dicerealms```

# Or use the CLI

```dicerealms start```

**Example Session:**

**Quick Start (Single-Player)**

```bash
# Run the game
python -m dicerealms

# Or use the CLI
dicerealms startalms server --port 8765

# Terminal 2: Connect as Player 1
dicerealms connect --host localhost --port 8765 --name Alice

# Terminal 3: Connect as Player 2
dicerealms connect --host localhost --port 8765 --name Bob**Multiplayer Flow Example:**
```

**Example Session:**

🎲 Entering DiceRealms. Type 'help' for commands; 'quit' to exit.
💡 Tip: Use 'name <your_name>' to set your character's name.

+Adventurer> name Alice
✨ Your name is now: Alice

+Alice> roll 2d6+1
2d6+1 -> 9 (Parts: [3, 5, 1])

+Alice> look
You are in a dark room. There is a table with a map on it. Exits: north, east.

+Alice> quit
👋 Goodbye!

## Multiplayer (Coming in M3)

### Terminal 1: Start the server
dicerealms server --port 8765

### Terminal 2: Connect as Player 1
dicerealms connect --host localhost --port 8765 --name Alice

### Terminal 3: Connect as Player 2
dicerealms connect --host localhost --port 8765 --name BobMultiplayer Client-Server
- **Server:** Manages shared game state, enforces turn order, broadcasts actions
- **Client:** Rich UI (output) + prompt-toolkit (input), connects via WebSocket
- **Protocol:** JSON-based WebSocket messages
- **Synchronization:** Turn-based with action announcements → wait → results

See the [Architecture Design Document](./docs/ARCHITECTURE.md) for detailed design.

---

## 📦 Dependencies

### Core
- **Rich** (≥14.1.0): Beautiful terminal output
- **Typer** (≥0.16.1): CLI framework
- **loguru** (≥0.7.3): Structured logging

### Coming in M3
- **prompt-toolkit** (≥3.0.0): Advanced input handling
- **websockets** (≥12.0): WebSocket client/server

### Development
- **pytest**: Testing framework
- **ruff**: Linting and formatting
- **pyright**: Type checking

---

## 🗺️ Roadmap

See [ROADMAP.md](./ROADMAP.md) for the high-level plan, or [MILESTONES.md](./MILESTONES.md) for detailed checklists.

**Current Focus:** M2 — Gameplay Basics (single-player polish)  
**Next Up:** M3 — Multiplayer Connectivity (the big leap!)

---

## 📄 License

This project is licensed under the [MIT License](./LICENSE).

**Note:** The project maintainers may also offer future releases under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0) to provide an explicit patent grant if that becomes relevant.

---

## 🤝 Contributing

This is an open project — PRs and ideas are welcome! 

### Getting Involved
1. Check [MILESTONES.md](./MILESTONES.md) for current tasks
2. Read [docs/PROJECT_STATE.md](./docs/PROJECT_STATE.md) for code structure
3. Run tests before submitting PRs
4. Follow the existing code style (ruff-formatted)

---

## 💬 Join the Realm

Questions? Ideas? Found a bug? Open an issue or start a discussion!

**Current Status:** Actively developing M2 (Gameplay Basics) with M3 (Multiplayer) design complete and ready for implementation.

---

## Multiplayer Flow Example:

### All players see this when Alice rolls:
┌─────────────────────────────────┐
│ 🎲 Alice is rolling 2d6...      │
│ [Spinner animation - 2 seconds]│
└─────────────────────────────────┘

### Then all players see:
┌─────────────────────────────────┐
│ Action Result                         │
│ Player:  Alice                  │
│ Action:  🎲 Roll Dice           │
│ Expression:  2d6                │
│ Result:  7                      │
│ Rolls:  [3, 4]                  │
└─────────────────────────────────┘

--- 

# 🧪 Development

## Running Tests

### Run all tests
```uv run pytest```

### With coverage
```uv run pytest --cov=dicerealms --cov-report=html```

### Run specific test file
```uv run pytest tests/test_core.py```

## Code Quality

### Lint
```uv run ruff check .```

### Format
```uv run ruff format .```

### Type check
```uv run pyright```

## Project Structure

dicerealms-python/
├── dicerealms/              # Main package
│   ├── __init__.py
│   ├── __main__.py          # Entry point
│   ├── cli.py               # Typer CLI commands
│   ├── core.py              # Dice rolling & core utilities
│   ├── player.py            # Player representation
│   ├── world.py             # World/room definitions
│   ├── engine.py            # Game engine (single-player)
│   ├── session.py           # Player session management
│   ├── console_frontend.py  # Console UI (single-player)
│   ├── server.py            # WebSocket server (M3) 🚧
│   └── client.py            # WebSocket client (M3) 🚧
├── examples/
│   └── quickstart.py        # Example script
├── tests/                   # Test suite
│   ├── test_core.py
│   ├── test_engine.py
│   └── ...
├── docs/
│   ├── milestones/          # Detailed milestone docs
│   │   ├── M1.md
│   │   ├── M2.md
│   │   └── ...
│   ├── ARCHITECTURE.md      # Multiplayer design (M3) 🚧
│   └── PROJECT_STATE.md
├── ROADMAP.md               # High-level roadmap
├── MILESTONES.md            # Milestone checklist
├── pyproject.toml           # Project config
└── README.md                # This file

---

## 🏗️ Architecture

Current (M1-M2): Single-Player

* Engine: Synchronous game loop with command handlers
* Session: Async session management with input queue
* Frontend: Console-based I/O with callback system

Coming (M3): Multiplayer Client-Server

* Server: Manages shared game state, enforces turn order, broadcasts actions
* Client: Rich UI (output) + prompt-toolkit (input), connects via WebSocket
* Protocol: JSON-based WebSocket messages
* Synchronization: Turn-based with action announcements → wait → results

See the Architecture Design Document for detailed design.

---

### 📦 Dependencies

Core
* Rich (≥14.1.0): Beautiful terminal output
* Typer (≥0.16.1): CLI framework
* loguru (≥0.7.3): Structured logging

Coming in M3

* prompt-toolkit (≥3.0.0): Advanced input handling
* websockets (≥12.0): WebSocket client/server

Development
* pytest: Testing framework
* ruff: Linting and formatting
* pyright: Type checking

---

### 🗺️ Roadmap

See ROADMAP.md for the high-level plan, or MILESTONES.md for detailed checklists.

Current Focus: M2 — Gameplay Basics (single-player polish)

Next Up: M3 — Multiplayer Connectivity (the big leap!)

---

### 📄 License

This project is licensed under the MIT License.

**Note:** The project maintainers may also offer future releases under the Apache License 2.0 to provide an explicit patent grant if that becomes relevant.

---

### 🤝 Contributing

This is an open project — PRs and ideas are welcome!

**Getting Involved**

1. Check MILESTONES.md for current tasks
2. Read docs/PROJECT_STATE.md for code structure
3. Run tests before submitting PRs
4. Follow the existing code style (ruff-formatted)

--- 

### 💬 Join the Realm

Questions? Ideas? Found a bug? Open an issue or start a discussion!

Current Status: Actively developing M2 (Gameplay Basics) with M3 (Multiplayer) design complete and ready for implementation.