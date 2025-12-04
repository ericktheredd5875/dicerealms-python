# 🛣️ DiceRealms Roadmap

DiceRealms is a **multiplayer, turn-based, dice-driven fantasy RPG** with beautiful terminal UIs.  
This roadmap lays out the planned evolution of the project at a high level.  
For detailed milestone tasks, see [MILESTONES.md](MILESTONES.md).

For the complete architecture design, see the [Multiplayer Architecture Design Document](./docs/ARCHITECTURE.md).

---

## 🎯 Phase 1: Core Foundations (Milestone 1) ✅
- [x] Establish Python package structure
- [x] Implement dice rolling, player, and world stubs
- [x] Functional CLI entrypoint (`python -m dicerealms`)
- [x] Unit test framework in place
- [x] Example quickstart script

**Status:** Complete

---

## 🎯 Phase 2: Gameplay Basics (Milestone 2)
- [ ] Room/world navigation system
- [ ] Player stats, inventory, and simple actions (look, move, roll, quit)
- [ ] Enhanced command parser for CLI input
- [ ] Rich terminal UI integration (output formatting)
- [ ] Playable single-player demo script (`examples/quickstart.py`)

**Focus:** Single-player experience with polished UI

---

## 🎯 Phase 3: Multiplayer Connectivity (Milestone 3) 🚀
**The Big Leap: Turn-Based Multiplayer with Synchronized Actions**

### Core Infrastructure
- [ ] WebSocket server implementation (`dicerealms/server.py`)
- [ ] WebSocket client implementation (`dicerealms/client.py`)
- [ ] Message protocol (JSON-based WebSocket frames)
- [ ] Connection handling and player session management

### Turn-Based System
- [ ] Turn manager (enforces one action at a time)
- [ ] Action announcement system (broadcast before execution)
- [ ] Synchronized waiting/animation (all clients pause together)
- [ ] Result broadcasting (all clients see results simultaneously)
- [ ] Turn status management (whose turn is it?)

### UI Integration
- [ ] Rich console integration for all output (tables, panels, colors)
- [ ] prompt-toolkit integration for advanced input (history, autocomplete)
- [ ] Synchronized spinner/progress indicators during actions
- [ ] Multi-player game state display (player list, room info, chat)

### Messaging
- [ ] Chat system (say, whisper, system messages)
- [ ] Real-time game state updates
- [ ] Error handling and user feedback

**Key Feature:** When Player1 rolls dice, ALL players see the announcement, wait together (2-second animation), then see the result simultaneously.

**Status:** Design complete, ready for implementation

---

## 🎯 Phase 4: Game Systems Expansion (Milestone 4)
- [ ] Dice-based combat system (turn-based, synchronized)
- [ ] Loot & item generation (rarity tiers: common/uncommon/rare/epic)
- [ ] Persistence (save/load player state, SQLite or JSON storage)
- [ ] Expanded world (first dungeon/realm with multiple rooms)
- [ ] Inventory management UI (Rich tables)
- [ ] Tests for combat, items, persistence

**Focus:** Core gameplay mechanics with multiplayer support

---

## 🎯 Phase 5: Observability & DevOps (Milestone 5)
- [ ] Structured logging (loguru integration)
- [ ] Metrics and counters for game actions
- [ ] Optional OpenTelemetry instrumentation
- [ ] CI/CD via GitHub Actions (lint, type-check, test, package build)
- [ ] Dockerfile & container setup
- [ ] Deployable dev server script
- [ ] Server health monitoring

**Focus:** Production readiness

---

## 🎯 Phase 6: Advanced Features (Milestone 6)
- [ ] NPCs & quests (basic AI-driven interactions)
- [ ] Scripting for rooms/encounters (YAML/JSON-based definitions)
- [ ] Admin/GM tools with override capabilities
- [ ] Enhanced Rich UI layouts (multi-panel views)
- [ ] Command autocomplete with game context
- [ ] Documentation site (MkDocs or Sphinx)
- [ ] Replay system (record and playback game sessions)

**Focus:** Rich gameplay and polish

---

## 📅 Future Ideas (Post-M6)
- **PvP Combat:** Player vs player battles with synchronized turns
- **Guilds & Groups:** Form parties and share adventures
- **In-Game Economy:** Trading system between players
- **Realm Expansions:** Procedurally generated worlds
- **Web Client:** Browser-based companion client (same protocol)
- **Mobile Support:** Terminal client for mobile devices
- **Discord/Slack Integration:** Dice-rolling bots for external platforms
- **Spectator Mode:** View-only clients for watching games
- **Modding Support:** Plugin system for custom actions/mechanics

---

## 🏗️ Architecture Highlights

### Client-Server Model
- **Server:** Manages game state, enforces turn order, processes actions
- **Clients:** Independent Rich UIs, each player connects from their terminal
- **Communication:** WebSocket-based JSON protocol

### Turn-Based Synchronization
1. Player submits action → Server receives
2. Server broadcasts announcement → ALL clients display
3. All clients show spinner/animation → Synchronized wait (2 seconds)
4. Server executes action → Broadcasts result
5. ALL clients display result → Turn advances

### UI Technology Stack
- **Rich:** All output rendering (tables, panels, colors, spinners)
- **prompt-toolkit:** Input handling (history, autocomplete, multi-line)
- **websockets:** Client-server communication
- **asyncio:** Non-blocking I/O

---

## 🔗 Related Docs
- [Milestones Overview](MILESTONES.md)  
- [Detailed Milestones](docs/milestones/)  
- [Architecture Design Document](./docs/ARCHITECTURE.md) *(to be created)*
- [Project State](docs/PROJECT_STATE.md)