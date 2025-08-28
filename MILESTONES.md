# 🗺️ DiceRealms Milestones

## M1 – Core Foundations
- [x] Project scaffolding (`dicerealms/`, tests/, examples/, pyproject.toml, README, license)  
- [x] Core game logic (dice rolls, player, world basics)  
- [x] CLI startup command (`python -m dicerealms`) fixed and functional  
- [x] Basic game loop with command input/output  
- [x] Unit tests for `core.py`, `player.py`, `world.py`  

➡️ [View details in `M1.md`](./docs/milestones/M1.md)

---

## M2 – Gameplay Basics
- [ ] Define rooms/world navigation (`world.py`)  
- [ ] Player stats, inventory, and simple actions (look, move, roll, quit)  
- [ ] Command parser to map text input to actions  
- [ ] Expanded tests for commands & interactions  
- [ ] Example script (`examples/quickstart.py`) fully playable  

➡️ [View details in `M2.md`](./docs/milestones/M2.md)

---

## M3 – Multiplayer Connectivity
- [ ] Introduce networking layer  
  - Option A: WebSocket server  
  - Option B: Telnet/SSH (fallback or first pass)  
- [ ] Player sessions and connection handling  
- [ ] Multiple players in the same world instance  
- [ ] Messaging system (say, whisper, system messages)  
- [ ] Basic authentication/identities  

➡️ [View details in `M3.md`](./docs/milestones/M3.md)

---

## M4 – Game Systems Expansion
- [ ] Combat system (dice-based)  
- [ ] Items & loot generation (common/uncommon/rare/epic)  
- [ ] Persistence (save/load player state, SQLite or JSON storage)  
- [ ] Expanded world with at least one dungeon/realm  
- [ ] Tests for combat, items, persistence  

➡️ [View details in `M4.md`](./docs/milestones/M4.md)

---

## M5 – Observability & DevOps
- [ ] Logging and metrics hooks (structured logging, counters for actions)  
- [ ] Add optional OpenTelemetry instrumentation  
- [ ] GitHub Actions: lint (ruff), type-check (pyright), test, package build  
- [ ] Dockerfile & basic container setup  
- [ ] Deployable dev server script  

➡️ [View details in `M5.md`](./docs/milestones/M5.md)

---

## M6 – Advanced Features
- [ ] NPCs & quests (basic AI-driven interactions)  
- [ ] Scripting for rooms/encounters (maybe YAML/JSON-based definitions)  
- [ ] Admin/GM commands  
- [ ] Polished CLI with color, styles, maybe Textual for richer UI  
- [ ] Documentation site (MkDocs or Sphinx)  

➡️ [View details in `M6.md`](./docs/milestones/M6.md)
