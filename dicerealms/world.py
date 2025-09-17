# SPDX-License-Identifier: MIT
# dicerealms/world.py
"""
World graph primitives for DiceRealms.

Design goals (M2):
- Lightweight graph representing rooms and exits (no external deps)
- Simple APIs used by the engine/session: look(), move(), neighbors()
- Deterministic data model suitable for later persistence (M3)
- Room-centric, direction-based navigation (N/E/S/W/U/D), extensible

Future-ready (not required for M2):
- Weighted edges (costs), locks/keys, visibility rules
- Zones/realms, procedural generation hooks
- Pathfinding helpers (basic BFS now; A* later if needed)
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field

# canonical lowercase strings: "north", "east", "south", "west", "up", "down"
Direction = str

# Opposite direction mapping for convenience when creating bidirectional exits
OPPOSITE: dict[Direction, Direction] = {
    "north": "south",
    "south": "north",
    "east": "west",
    "west": "east",
    "up": "down",
    "down": "up",
}


@dataclass(slots=True)
class Exit:
    """Represents a directed edge from one room to another.

    Attributes:
        to_room: ID of the destination room
        description: Optional text shown when using this exit
        locked: Whether this exit is currently locked
    """

    to_room: str
    description: str | None = None
    locked: bool = False


@dataclass(slots=True)
class Room:
    """Node in the world graph.

    Attributes:
        id: Stable, unique ID (slug-like), used as graph key
        name: Display name
        description: Long-form description
        exits: mapping direction -> Exit
    """

    id: str
    name: str
    description: str = ""
    exits: dict[Direction, Exit] = field(default_factory=dict)

    def add_exit(
        self,
        direction: Direction,
        to_room: str,
        *,
        description: str | None = None,
        locked: bool = False,
    ) -> None:
        d = direction.lower()
        self.exits[d] = Exit(to_room=to_room, description=description, locked=locked)

    def neighbor(self) -> dict[Direction, str]:
        return {d: ex.to_room for d, ex in self.exits.items() if not ex.locked}


class World:
    """A lightweight, directional graph of rooms.

    Public API expected by engine/session:
        - current_room(player_room_id) -> Room | None
        - look(room_id) -> str
        - move(room_id, direction) -> tuple[new_room_id | None, message]
        - neighbors(room_id) -> dict[direction, room_id]
        - find_path(start_id, goal_id) -> list[room_id] | None (BFS)
    """

    def __init__(self, *, title: str = "DiceRealms") -> None:
        self.title = title
        self._rooms: dict[str, Room] = {}

    # --- Mutation ---
    def add_room(self, room: Room) -> None:
        if room.id in self._rooms:
            raise ValueError(f"Room {room.id} already exists")

        self._rooms[room.id] = room

    def add(self, room_id: str, name: str, description: str = "") -> Room:
        room = Room(id=room_id, name=name, description=description)
        self.add_room(room)
        return room

    def connect(
        self,
        a_id: str,
        direction: Direction,
        b_id: str,
        *,
        bidir: bool = True,
        description: str | None = None,
        back_description: str | None = None,
        locked: bool = False,
        back_locked: bool | None = None,
    ) -> None:
        """
        Create an exit from a -> b; optionally also b -> a using the opposite direction.

        If bidir is True and back_locked is None, the back edge inherits `locked`.
        """
        a = self.require_room(a_id)
        b = self.require_room(b_id)
        a.add_exit(direction, b_id, description=description, locked=locked)
        if bidir:
            back_dir = OPPOSITE.get(direction.lower())
            if not back_dir:
                raise ValueError(f"No opposite direction for '{direction}'")

            b.add_exit(
                back_dir,
                a_id,
                description=back_description,
                locked=locked if back_locked is None else back_locked,
            )

    # --- Queries ---
    def has_room(self, room_id: str) -> bool:
        return room_id in self._rooms

    def require_room(self, room_id: str) -> Room:
        try:
            return self._rooms[room_id]
        except KeyError:
            raise KeyError(f"Room not found: {room_id}") from None

    def current_room(self, room_id: str) -> Room | None:
        return self._rooms.get(room_id)

    def look(self, room_id: str) -> str:
        room = self.require_room(room_id)
        lines: list[str] = [room.name, "", room.description.strip()]
        exits = room.neighbor()

        if exits:
            pretty = ", ".join(sorted(exits.keys()))
            lines += ["", f"Exits: {pretty}"]
        else:
            lines += ["", "No obvious exits."]

        return "\n".join(lines).strip()

    def neighbors(self, room_id: str) -> dict[Direction, str]:
        return self.require_room(room_id).neighbor()

    def move(self, room_id: str, direction: Direction) -> tuple[str | None, str]:
        d = direction.lower()
        room = self.require_room(room_id)
        ex = room.exits.get(d)
        if not ex:
            return None, f"You can't go {d}."

        if ex.locked:
            return None, f"{d} is locked."

        dest = self.require_room(ex.to_room)
        return dest.id, f"You move {d} to {dest.name}."

    def rooms(self) -> Iterable[Room]:
        return self._rooms.values()

    # --- Pathfinding (simple BFS for now) ---
    def find_path(self, start_id: str, goal_id: str) -> list[str] | None:
        if start_id == goal_id:
            return [start_id]

        if start_id not in self._rooms or goal_id not in self._rooms:
            return None

        from collections import deque

        q = deque([start_id])
        come_from: dict[str, str | None] = {start_id: None}
        while q:
            cur = q.popleft()
            for nxt in self.neighbors(cur).values():
                if nxt not in come_from:
                    come_from[nxt] = cur
                    if nxt == goal_id:
                        path: list[str] = [nxt]
                        while cur is not None:
                            path.append(cur)
                            cur = come_from[cur]
                        path.reverse()
                        return path
                    q.append(nxt)
        return None

    # --- Serialization helpers (for M3) ---
    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "rooms": [
                {
                    "id": r.id,
                    "name": r.name,
                    "description": r.description,
                    "exits": {
                        d: {
                            "to": ex.to_room,
                            "description": ex.description,
                            "locked": ex.locked,
                        }
                        for d, ex in r.exits.items()
                    },
                }
                for r in self.rooms()
            ],
        }

    @classmethod
    def from_dict(cls, data: dict) -> World:
        w = cls(title=data.get("title", "DiceRealms"))
        for rdata in data.get("rooms", []):
            r = Room(
                id=rdata["id"],
                name=rdata.get("name", rdata["id"]),
                description=rdata.get("description", ""),
            )
            for d, ex in rdata.get("exits", {}).items():
                r.add_exit(
                    d,
                    to_room=ex["to"],
                    description=ex.get("description"),
                    locked=ex.get("locked", False),
                )
            w.add_room(r)
        return w


# --- Small starter map for examples/tests ---
def load_default_world() -> World:
    """Create a tiny, pleasant starter map.

    Layout (bidir unless noted):
        Town Square --north--> North Road --north--> Gate (locked)
            |\
            | south
            v
            Tavern --east--> Market

    """
    w = World(title="DiceRealms – Beginner's Vale")

    w.add(
        "town_square",
        "Town Square",
        "The bustling heart of the village. A fountain burbles cheerfully.",
    )
    w.add(
        "tavern",
        "Tavern",
        "Warm firelight and the smell of stew. Adventurers trade stories here.",
    )
    w.add(
        "market",
        "Market",
        "Stalls clutter the lane with trinkets, tools, and a suspiciously shiny apple.",
    )
    w.add(
        "north_road",
        "North Road",
        "A dirt road lined with wind-bent trees leads toward old stone walls.",
    )
    w.add(
        "gate",
        "Old City Gate",
        "Massive wooden doors bound with iron. They appear firmly shut.",
    )

    w.connect("town_square", "south", "tavern")
    w.connect("tavern", "east", "market")
    w.connect("town_square", "north", "north_road")
    # One-way locked exit at the gate from north_road -> gate (locked); no back edge
    w.connect(
        "north_road",
        "north",
        "gate",
        bidir=False,
        locked=True,
        description="The gate is shut tight.",
    )

    return w


__all__ = [
    "Direction",
    "Exit",
    "Room",
    "World",
    "load_default_world",
]
