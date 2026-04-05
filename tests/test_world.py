# SPDX-License-Identifier: MIT
"""Tests for World graph navigation."""
import pytest

from dicerealms.world import Exit, Room, World, load_default_world

class TestRoom:

    def test_add_exit(self):
        room = Room(id="a", name="A")
        room.add_exit("north", "b")
        assert "north" in room.exits
        assert room.exits["north"].to_room == "b"

    def test_neighbor_excludes_locked(self):
        room = Room(id="a", name="A")
        room.add_exit("north", "b")
        room.add_exit("east", "c", locked=True)
        neighbors = room.neighbor()
        assert "north" in neighbors
        assert "east" not in neighbors


class TestWorld:

    @pytest.fixture
    def world(self):
        w = World()
        w.add("a", "Room A")
        w.add("b", "Room B")
        w.add("c", "Room C")
        w.connect("a", "north", "b")
        return w

    def test_add_duplicate_room_raises(self, world):
        with pytest.raises(ValueError):
            world.add("a", "Duplicate")

    def test_connect_creates_bidirectional_exits(self, world):
        assert world.require_room("a").exits["north"].to_room == "b"
        assert world.require_room("b").exits["south"].to_room == "a"

    def test_move_success(self, world):
        new_id, msg = world.move("a", "north")
        assert new_id == "b"
        assert "b" in msg.lower() or "Room B" in msg

    def test_move_invalid_direction(self, world):
        new_id, msg = world.move("a", "east")
        assert new_id is None
        assert "can't go" in msg.lower()

    def test_move_locked_exit(self, world):
        world.connect("a", "east", "c", locked=True)
        new_id, msg = world.move("a", "east")
        assert new_id is None
        assert "locked" in msg.lower()

    def test_look_includes_name_description_exits(self, world):
        result = world.look("a")
        assert "Room A" in result
        assert "north" in result

    def test_require_room_missing_raises(self, world):
        with pytest.raises(KeyError):
            world.require_room("nonexistent")

    def test_find_path_direct(self, world):
        path = world.find_path("a", "b")
        assert path == ["a", "b"]

    def test_find_path_no_route(self, world):
        path = world.find_path("a", "c")  # c only connects back to b
        assert path is None

    def test_find_path_same_room(self, world):
        assert world.find_path("a", "a") == ["a"]

    def test_serialization_roundtrip(self, world):
        data = world.to_dict()
        restored = World.from_dict(data)
        assert restored.has_room("a")
        assert restored.has_room("b")
        assert restored.require_room("a").exits["north"].to_room == "b"


class TestLoadDefaultWorld:

    def test_has_expected_rooms(self):
        w = load_default_world()
        for room_id in ["town_square", "tavern", "market", "north_road", "gate"]:
            assert w.has_room(room_id)

    def test_town_square_connects_south_to_tavern(self):
        w = load_default_world()
        new_id, _ = w.move("town_square", "south")
        assert new_id == "tavern"

    def test_gate_is_locked(self):
        w = load_default_world()
        new_id, msg = w.move("north_road", "north")
        assert new_id is None
        assert "locked" in msg.lower()