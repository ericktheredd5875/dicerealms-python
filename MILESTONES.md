## MILESTONES.md

# 🗺️ DiceRealms Milestones

This document tracks the detailed milestone checklists for DiceRealms development.  
For high-level roadmap, see [ROADMAP.md](./ROADMAP.md).

---

## M1 – Core Foundations ✅

**Status:** Complete  
**Focus:** Basic single-player game loop with dice rolling

- [x] Project scaffolding (`dicerealms/`, tests/, examples/, pyproject.toml, README, license)
- [x] Core game logic (dice rolls, player, world basics)
- [x] CLI startup command (`python -m dicerealms`) fixed and functional
- [x] Basic game loop with command input/output
- [x] Unit tests for `core.py`, `player.py`, `world.py`
- [x] Session management with async I/O
- [x] Console frontend with callback system

➡️ [View details in `M1.md`](./docs/milestones/M1.md)

---

## M2 – Gameplay Basics 🚧

**Status:** In Progress  
**Focus:** Single-player experience with polished UI

### World & Navigation
- [ ] Define rooms/world navigation (`world.py`)
- [ ] Room descriptions and exit system
- [ ] Movement commands (north, south, east, west, etc.)
- [ ] Room state management

### Player Systems
- [ ] Player stats (HP, MP, level, etc.)
- [ ] Inventory system (items, equipment)
- [ ] Character progression basics

### Commands & Actions
- [ ] Enhanced command parser
- [ ] Look command (detailed room descriptions)
- [ ] Move command (room transitions)
- [ ] Inventory commands (inventory, equip, use)
- [ ] Help system improvements

### UI Enhancement
- [ ] Rich integration for output (tables, panels, colors)
- [ ] Basic Rich formatting for game messages
- [ ] Improved command feedback

### Testing & Examples
- [ ] Expanded tests for commands & interactions
- [ ] Example script (`examples/quickstart.py`) fully playable
- [ ] Integration tests for game flow

➡️ [View details in `M2.md`](./docs/milestones/M2.md)

---

## M3 – Multiplayer Connectivity 🎯

**Status:** Design Complete, Ready for Implementation  
**Focus:** Turn-based multiplayer with synchronized actions

### Server Infrastructure
- [ ] Create `dicerealms/server.py` with WebSocket server
- [ ] Connection handling (connect, disconnect, reconnect)
- [ ] Player session management on server
- [ ] Message routing and broadcast system
- [ ] Error handling and connection recovery

### Client Infrastructure
- [ ] Create `dicerealms/client.py` with WebSocket client
- [ ] Connection management (connect, disconnect, auto-reconnect)
- [ ] Message sending and receiving
- [ ] Client state management

### Message Protocol
- [ ] Define JSON message format
- [ ] Action messages (roll, move, look, etc.)
- [ ] Chat messages (say, whisper, system)
- [ ] Game state messages (player list, room info)
- [ ] Turn status messages
- [ ] Error messages

### Turn-Based System
- [ ] Turn manager (track current player, enforce order)
- [ ] Action announcement system
  - [ ] Broadcast action before execution
  - [ ] All clients receive and display announcement
- [ ] Synchronized waiting/animation
  - [ ] Server-side delay (2 seconds for dramatic effect)
  - [ ] Client-side spinner/progress indicators
  - [ ] All clients wait together
- [ ] Action execution and result broadcasting
  - [ ] Server processes action
  - [ ] Broadcast result to all clients
  - [ ] All clients display result simultaneously
- [ ] Turn advancement
  - [ ] Next player selection
  - [ ] Turn status updates

### UI Integration
- [ ] Rich console integration
  - [ ] Action announcement panels
  - [ ] Result display panels
  - [ ] Player list tables
  - [ ] Room information display
  - [ ] Chat message formatting
- [ ] prompt-toolkit integration
  - [ ] Input handling with history
  - [ ] Command autocomplete
  - [ ] Turn-based input enabling/disabling
  - [ ] Multi-line input support
- [ ] Synchronized animations
  - [ ] Spinner during action execution
  - [ ] Progress indicators
  - [ ] Visual feedback for all players

### Messaging System
- [ ] Chat commands (say, whisper)
- [ ] System messages (player joins, leaves, etc.)
- [ ] Message broadcasting to room
- [ ] Private messaging (whisper)

### Testing
- [ ] Unit tests for server components
- [ ] Unit tests for client components
- [ ] Integration tests (2+ clients connected)
- [ ] Synchronization tests (verify all clients see actions)
- [ ] Turn management tests
- [ ] Connection/disconnection tests

### Documentation
- [ ] Architecture design document
- [ ] Message protocol specification
- [ ] Server setup guide
- [ ] Client usage guide
- [ ] Multiplayer examples

➡️ [View details in `M3.md`](./docs/milestones/M3.md)  
➡️ [Architecture Design Document](./docs/ARCHITECTURE.md) *(to be created)*

**Key Success Criteria:**
- ✅ Two players can connect simultaneously
- ✅ When Player1 acts, Player2 sees announcement BEFORE execution
- ✅ Both players see synchronized spinner/wait during action
- ✅ Both players see result simultaneously
- ✅ Turn-based: only current player can input commands
- ✅ Rich UI renders beautifully on both clients

---

## M4 – Game Systems Expansion

**Status:** Planned  
**Focus:** Core gameplay mechanics with multiplayer support

### Combat System
- [ ] Turn-based combat mechanics
- [ ] Attack, defend, use item actions
- [ ] Dice-based damage calculation
- [ ] HP/MP management
- [ ] Combat UI (Rich panels for battle state)
- [ ] Synchronized combat actions (all players see battle)

### Items & Loot
- [ ] Item system (weapons, armor, consumables)
- [ ] Rarity tiers (common/uncommon/rare/epic)
- [ ] Loot generation system
- [ ] Item stats and effects
- [ ] Inventory management UI (Rich tables)

### Persistence
- [ ] Save/load player state
- [ ] Storage backend (SQLite or JSON)
- [ ] Character persistence across sessions
- [ ] World state persistence (optional)

### World Expansion
- [ ] First dungeon/realm with multiple rooms
- [ ] Room connections and navigation
- [ ] Room-specific descriptions and events
- [ ] World state management

### Testing
- [ ] Combat system tests
- [ ] Item system tests
- [ ] Persistence tests
- [ ] Integration tests with multiplayer

➡️ [View details in `M4.md`](./docs/milestones/M4.md)

---

## M5 – Observability & DevOps

**Status:** Planned  
**Focus:** Production readiness

### Logging & Metrics
- [ ] Structured logging (loguru integration)
- [ ] Action counters and metrics
- [ ] Performance monitoring
- [ ] Optional OpenTelemetry instrumentation
- [ ] Server health endpoints

### CI/CD
- [ ] GitHub Actions workflow
  - [ ] Lint (ruff)
  - [ ] Type check (pyright)
  - [ ] Tests (pytest)
  - [ ] Coverage reporting
  - [ ] Package build
- [ ] Automated testing on PRs
- [ ] Release automation

### Deployment
- [ ] Dockerfile for server
- [ ] Docker Compose for local development
- [ ] Deployable dev server script
- [ ] Environment configuration
- [ ] Server startup/shutdown procedures

### Documentation
- [ ] Deployment guide
- [ ] Server configuration docs
- [ ] Monitoring and observability guide

➡️ [View details in `M5.md`](./docs/milestones/M5.md)

---

## M6 – Advanced Features

**Status:** Planned  
**Focus:** Rich gameplay and polish

### NPCs & Quests
- [ ] NPC system (non-player characters)
- [ ] Basic AI-driven interactions
- [ ] Quest system (objectives, rewards)
- [ ] Dialogue system
- [ ] NPC actions in turn-based system

### Scripting
- [ ] Room/encounter definitions (YAML/JSON)
- [ ] Event scripting system
- [ ] Conditional logic for rooms
- [ ] Scripted encounters

### Admin/GM Tools
- [ ] Admin commands (override, spawn, etc.)
- [ ] GM mode (game master tools)
- [ ] Player management commands
- [ ] World editing tools

### UI Polish
- [ ] Enhanced Rich layouts (multi-panel views)
- [ ] Command autocomplete with game context
- [ ] Better visual feedback
- [ ] Customizable UI themes
- [ ] Optional Textual integration for advanced UIs

### Documentation
- [ ] Documentation site (MkDocs or Sphinx)
- [ ] API documentation
- [ ] Gameplay guides
- [ ] Modding documentation

### Additional Features
- [ ] Replay system (record and playback)
- [ ] Spectator mode (view-only clients)
- [ ] Game statistics and achievements

➡️ [View details in `M6.md`](./docs/milestones/M6.md)

---

## 📊 Progress Summary

- **M1:** ✅ Complete (Core Foundations)
- **M2:** 🚧 In Progress (Gameplay Basics)
- **M3:** 🎯 Design Complete (Multiplayer Connectivity)
- **M4:** 📋 Planned (Game Systems Expansion)
- **M5:** 📋 Planned (Observability & DevOps)
- **M6:** 📋 Planned (Advanced Features)

---

## 🔗 Related Docs
- [Roadmap Overview](ROADMAP.md)
- [Detailed Milestones](docs/milestones/)
- [Project State](docs/PROJECT_STATE.md)