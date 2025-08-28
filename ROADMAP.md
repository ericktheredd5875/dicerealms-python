# 🛣️ DiceRealms Roadmap

DiceRealms is a multiplayer, dice-driven fantasy RPG world.  
This roadmap lays out the planned evolution of the project at a high level.  
For detailed milestone tasks, see [MILESTONES.md](MILESTONES.md).

---

## 🎯 Phase 1: Core Foundations (Milestone 1)
- Establish Python package structure
- Implement dice rolling, player, and world stubs
- Functional CLI entrypoint (`python -m dicerealms`)
- Unit test framework in place
- Example quickstart script

---

## 🎯 Phase 2: Gameplay Basics (Milestone 2)
- Room/world navigation
- Player stats, inventory, and simple actions
- Command parser for CLI input
- Playable demo script (`examples/quickstart.py`)

---

## 🎯 Phase 3: Multiplayer Connectivity (Milestone 3)
- Networking layer (WebSocket preferred, Telnet/SSH optional)
- Multiple concurrent players in shared world
- Messaging system (say, whisper, system messages)
- Player session/authentication support

---

## 🎯 Phase 4: Game Systems Expansion (Milestone 4)
- Dice-based combat system
- Loot & item generation (rarity tiers)
- Persistence (save/load player state)
- Expanded world (first dungeon/realm)

---

## 🎯 Phase 5: Observability & DevOps (Milestone 5)
- Structured logging, counters, optional OpenTelemetry
- CI/CD via GitHub Actions (lint, type-check, test, package build)
- Dockerfile & container setup
- Deployable dev server

---

## 🎯 Phase 6: Advanced Features (Milestone 6)
- NPCs & quests (basic AI interactions)
- Scripting for rooms and encounters
- Admin/GM tools
- Polished CLI with color/styles (Textual optional)
- Documentation site (MkDocs or Sphinx)

---

## 📅 Future Ideas (Post-M6)
- PvP combat and guilds
- In-game economy and trading
- Realm expansions & procedurally generated worlds
- Web-based companion client (browser play)
- Integration with dice-rolling bots (Discord/Slack/etc.)

---

## 🔗 Related Docs
- [Milestones Overview](MILESTONES.md)  
- [Detailed Milestones](docs/milestones/)  
