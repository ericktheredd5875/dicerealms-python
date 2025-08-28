# 🎲 DiceRealms (Python)

**DiceRealms** is a modern, multiplayer MUD-style roleplaying platform using a structured protocol inspired by classic MUDs and tabletop RPGs like Dungeons & Dragons.

Built from the ground up to support immersive text-based storytelling, structured MCP commands, and group-based roleplaying adventures — DiceRealms lets you emote, speak, roll, and act in shared virtual spaces.

This project is in active development. Current milestone: **M1 — Core Foundations**.

---
<!-- [![codecov](https://codecov.io/gh/ericktheredd5875/dicerealms/graph/badge.svg?token=8Q1IB3P0UL)](https://codecov.io/gh/ericktheredd5875/dicerealms) -->
---

## 👩‍👨 Features

* 🧹 **Structured MCP Protocol**: Custom command parsing with tags like `mcp-emote`, `mcp-roll`, and `mcp-say`.
* 🎝️ **Room-Based Group Play**: Join others in shared scenes and interact in real time.
* 🎲 **Dice Rolling**: Support for expressions like `1d20+5`, with critical success/failure detection.
* 🗣️ **Emotes & In-Character Speech**: Express yourself with structured roleplay.
* 🔄 **Extensible Architecture**: Future-ready for AI integration, persistence, and DM tools.

---

## 🚀 Getting Started

### Prerequisites

* Python 3.13
* Git
* uv 
* (Optional) Telnet or netcat for testing

### Clone and Run

```bash
git clone https://github.com/yourname/dicerealms-python.git
cd dicerealms-python
uv venv
uv pip install -e .

# Run the Game:
uv run dicerealms start

# Example Usage
dicerealms
🎲 Welcome to DiceRealms!
Type 'help' for commands.

> roll 2d6+1
2d6+1 → 9 (parts: [3, 5])

> look
You are in a dimly lit hall. Exits: north, east.

> quit
Goodbye, adventurer! 👋

```

### 🧪 Development

```bash
# Run Tests
uv run pytest

# Lint and Format
uv run ruff check .
uv run ruff format .    

```

---

### Connect to the Server

To Come

---

## 📂 Project Structure

```Bash
dicerealms-python/
├── dicerealms/       # Main package
│   ├── __init__.py
│   ├── __main__.py
│   ├── core.py       # Dice and core utilities
│   ├── player.py     # Player representation
│   ├── world.py      # World placeholders
│   ├── engine.py     # Game loop
│   └── session.py    # Player session orchestration
├── examples/
│   └── quickstart.py
├── tests/
│   └── test_core.py
├── docs/
│   ├── milestones/
│   │   ├── M1.md
│   │   ├── M2.md
│   │   └── ...
│   └── PROJECT_STATE.md
├── ROADMAP.md
├── MILESTONES.md
├── pyproject.toml
├── LICENSE
└── README.md
```

---

## License

This project is licensed under the [MIT License](./LICENSE).

**Note:** The project maintainers may also offer future releases under the
[Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0) to provide
an explicit patent grant if that becomes relevant.

---

## 🧠 Future Roadmap

See [Roadmap](./ROADMAP.md) or [Milestones](./MILESTONES.md)

---

## 💬 Join the Realm

This is an open project — PRs and ideas are welcome!