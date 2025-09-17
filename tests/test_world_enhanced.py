# tests/test_world_enhanced.py
# SPDX-License-Identifier: MIT

import pytest

from dicerealms.world import OPPOSITE, Direction, Exit, Room, World, load_default_world


def test_opposite_directions():
    """Test the OPPOSITE direction mapping."""
    assert OPPOSITE["north"] == "south"
    assert OPPOSITE["south"] == "north"
    assert OPPOSITE["east"] == "west"
    assert OPPOSITE["west"] == "east"
    assert OPPOSITE["up"] == "down"
    assert OPPOSITE["down"] == "up"


def test_exit_creation():
    """Test Exit dataclass creation."""
    exit_obj = Exit(to_room="room2", description="A door", locked=False)

    assert exit_obj.to_room == "room2"
    assert exit_obj.description == "A door"
    assert exit_obj.locked is False


def test_exit_defaults():
    """Test Exit with default values."""
    exit_obj = Exit(to_room="room2")

    assert exit_obj.to_room == "room2"
    assert exit_obj.description is None
    assert exit_obj.locked is False


def test_room_creation():
    """Test Room dataclass creation."""
    room = Room(id="test_room", name="Test Room", description="A test room")

    assert room.id == "test_room"
    assert room.name == "Test Room"
    assert room.description == "A test room"
    assert room.exits == {}


def test_room_defaults():
    """Test Room with default values."""
    room = Room(id="test_room", name="Test Room")

    assert room.id == "test_room"
    assert room.name == "Test Room"
    assert room.description == ""
    assert room.exits == {}


def test_room_add_exit():
    """Test adding exits to a room."""
    room = Room(id="test_room", name="Test Room")

    room.add_exit("north", "room2", description="A door", locked=False)

    assert "north" in room.exits
    exit_obj = room.exits["north"]
    assert exit_obj.to_room == "room2"
    assert exit_obj.description == "A door"
    assert exit_obj.locked is False


def test_room_add_exit_locked():
    """Test adding locked exits to a room."""
    room = Room(id="test_room", name="Test Room")

    room.add_exit("south", "room3", locked=True)

    assert "south" in room.exits
    exit_obj = room.exits["south"]
    assert exit_obj.to_room == "room3"
    assert exit_obj.locked is True


def test_room_add_exit_case_insensitive():
    """Test that exit directions are normalized to lowercase."""
    room = Room(id="test_room", name="Test Room")

    room.add_exit("NORTH", "room2")

    assert "north" in room.exits
    assert "NORTH" not in room.exits


def test_room_neighbor_excludes_locked():
    """Test that neighbor() excludes locked exits."""
    room = Room(id="test_room", name="Test Room")

    room.add_exit("north", "room2", locked=False)
    room.add_exit("south", "room3", locked=True)

    neighbors = room.neighbor()

    assert "north" in neighbors
    assert "south" not in neighbors
    assert neighbors["north"] == "room2"


def test_world_creation():
    """Test World creation."""
    world = World()

    assert world.title == "DiceRealms"
    assert len(world._rooms) == 0


def test_world_creation_with_title():
    """Test World creation with custom title."""
    world = World(title="Custom World")

    assert world.title == "Custom World"


def test_world_add_room():
    """Test adding rooms to world."""
    world = World()
    room = Room(id="test_room", name="Test Room")

    world.add_room(room)

    assert "test_room" in world._rooms
    assert world._rooms["test_room"] == room


def test_world_add_room_duplicate():
    """Test adding duplicate room raises error."""
    world = World()
    room1 = Room(id="test_room", name="Test Room 1")
    room2 = Room(id="test_room", name="Test Room 2")

    world.add_room(room1)

    with pytest.raises(ValueError, match="Room test_room already exists"):
        world.add_room(room2)


def test_world_add_method():
    """Test the add method for creating and adding rooms."""
    world = World()

    room = world.add("test_room", "Test Room", "A test room")

    assert room.id == "test_room"
    assert room.name == "Test Room"
    assert room.description == "A test room"
    assert "test_room" in world._rooms


def test_world_has_room():
    """Test checking if room exists."""
    world = World()
    world.add("test_room", "Test Room")

    assert world.has_room("test_room") is True
    assert world.has_room("nonexistent") is False


def test_world_require_room():
    """Test requiring a room that exists."""
    world = World()
    room = world.add("test_room", "Test Room")

    retrieved_room = world.require_room("test_room")
    assert retrieved_room == room


def test_world_require_room_missing():
    """Test requiring a room that doesn't exist."""
    world = World()

    with pytest.raises(KeyError, match="Room not found: nonexistent"):
        world.require_room("nonexistent")


def test_world_current_room():
    """Test getting current room."""
    world = World()
    room = world.add("test_room", "Test Room")

    current = world.current_room("test_room")
    assert current == room

    current = world.current_room("nonexistent")
    assert current is None


def test_world_connect_bidirectional():
    """Test connecting rooms bidirectionally."""
    world = World()
    world.add("room1", "Room 1")
    world.add("room2", "Room 2")

    world.connect("room1", "north", "room2")

    # Check forward connection
    assert "north" in world._rooms["room1"].exits
    assert world._rooms["room1"].exits["north"].to_room == "room2"

    # Check backward connection
    assert "south" in world._rooms["room2"].exits
    assert world._rooms["room2"].exits["south"].to_room == "room1"


def test_world_connect_unidirectional():
    """Test connecting rooms unidirectionally."""
    world = World()
    world.add("room1", "Room 1")
    world.add("room2", "Room 2")

    world.connect("room1", "north", "room2", bidir=False)

    # Check forward connection
    assert "north" in world._rooms["room1"].exits
    assert world._rooms["room1"].exits["north"].to_room == "room2"

    # Check no backward connection
    assert "south" not in world._rooms["room2"].exits


def test_world_connect_with_descriptions():
    """Test connecting rooms with descriptions."""
    world = World()
    world.add("room1", "Room 1")
    world.add("room2", "Room 2")

    world.connect(
        "room1",
        "north",
        "room2",
        description="A wooden door",
        back_description="A stone archway",
    )

    assert world._rooms["room1"].exits["north"].description == "A wooden door"
    assert world._rooms["room2"].exits["south"].description == "A stone archway"


def test_world_connect_with_locks():
    """Test connecting rooms with locks."""
    world = World()
    world.add("room1", "Room 1")
    world.add("room2", "Room 2")

    world.connect("room1", "north", "room2", locked=True)

    assert world._rooms["room1"].exits["north"].locked is True
    assert world._rooms["room2"].exits["south"].locked is True


def test_world_connect_with_different_back_lock():
    """Test connecting rooms with different back lock status."""
    world = World()
    world.add("room1", "Room 1")
    world.add("room2", "Room 2")

    world.connect("room1", "north", "room2", locked=True, back_locked=False)

    assert world._rooms["room1"].exits["north"].locked is True
    assert world._rooms["room2"].exits["south"].locked is False


def test_world_connect_invalid_direction():
    """Test connecting with invalid direction."""
    world = World()
    world.add("room1", "Room 1")
    world.add("room2", "Room 2")

    with pytest.raises(ValueError, match="No opposite direction for 'invalid'"):
        world.connect("room1", "invalid", "room2")


def test_world_connect_missing_room():
    """Test connecting with missing room."""
    world = World()
    world.add("room1", "Room 1")

    with pytest.raises(KeyError, match="Room not found: room2"):
        world.connect("room1", "north", "room2")


def test_world_look():
    """Test looking at a room."""
    world = World()
    world.add("test_room", "Test Room", "A test room description")
    world.add("room2", "Room 2")
    world.connect("test_room", "north", "room2")

    result = world.look("test_room")

    assert "Test Room" in result
    assert "A test room description" in result
    assert "Exits: north" in result


def test_world_look_no_exits():
    """Test looking at a room with no exits."""
    world = World()
    world.add("test_room", "Test Room", "A test room description")

    result = world.look("test_room")

    assert "Test Room" in result
    assert "A test room description" in result
    assert "No obvious exits." in result


def test_world_look_multiple_exits():
    """Test looking at a room with multiple exits."""
    world = World()
    world.add("test_room", "Test Room")
    world.add("room2", "Room 2")
    world.add("room3", "Room 3")
    world.connect("test_room", "north", "room2")
    world.connect("test_room", "south", "room3")

    result = world.look("test_room")

    assert "Exits: north, south" in result


def test_world_neighbors():
    """Test getting neighbors of a room."""
    world = World()
    world.add("test_room", "Test Room")
    world.add("room2", "Room 2")
    world.add("room3", "Room 3")
    world.connect("test_room", "north", "room2")
    world.connect("test_room", "south", "room3", locked=True)

    neighbors = world.neighbors("test_room")

    assert "north" in neighbors
    assert "south" not in neighbors
    assert neighbors["north"] == "room2"


def test_world_move_success():
    """Test successful room movement."""
    world = World()
    world.add("room1", "Room 1")
    world.add("room2", "Room 2")
    world.connect("room1", "north", "room2")

    new_room, message = world.move("room1", "north")

    assert new_room == "room2"
    assert "move north" in message
    assert "Room 2" in message


def test_world_move_invalid_direction():
    """Test movement in invalid direction."""
    world = World()
    world.add("room1", "Room 1")

    new_room, message = world.move("room1", "north")

    assert new_room is None
    assert "can't go north" in message


def test_world_move_locked_exit():
    """Test movement through locked exit."""
    world = World()
    world.add("room1", "Room 1")
    world.add("room2", "Room 2")
    world.connect("room1", "north", "room2", locked=True)

    new_room, message = world.move("room1", "north")

    assert new_room is None
    assert "north is locked" in message


def test_world_move_case_insensitive():
    """Test that movement directions are case insensitive."""
    world = World()
    world.add("room1", "Room 1")
    world.add("room2", "Room 2")
    world.connect("room1", "north", "room2")

    new_room, message = world.move("room1", "NORTH")

    assert new_room == "room2"
    assert "move north" in message


def test_world_rooms():
    """Test getting all rooms."""
    world = World()
    room1 = world.add("room1", "Room 1")
    room2 = world.add("room2", "Room 2")

    rooms = list(world.rooms())

    assert len(rooms) == 2
    assert room1 in rooms
    assert room2 in rooms


def test_world_find_path_same_room():
    """Test finding path to same room."""
    world = World()
    world.add("room1", "Room 1")

    path = world.find_path("room1", "room1")

    assert path == ["room1"]


def test_world_find_path_direct_connection():
    """Test finding path with direct connection."""
    world = World()
    world.add("room1", "Room 1")
    world.add("room2", "Room 2")
    world.connect("room1", "north", "room2")

    path = world.find_path("room1", "room2")

    assert path == ["room1", "room2"]


def test_world_find_path_multiple_hops():
    """Test finding path with multiple hops."""
    world = World()
    world.add("room1", "Room 1")
    world.add("room2", "Room 2")
    world.add("room3", "Room 3")
    world.connect("room1", "north", "room2")
    world.connect("room2", "north", "room3")

    path = world.find_path("room1", "room3")

    assert path == ["room1", "room2", "room3"]


def test_world_find_path_no_path():
    """Test finding path when no path exists."""
    world = World()
    world.add("room1", "Room 1")
    world.add("room2", "Room 2")
    # No connection between rooms

    path = world.find_path("room1", "room2")

    assert path is None


def test_world_find_path_missing_room():
    """Test finding path with missing room."""
    world = World()
    world.add("room1", "Room 1")

    path = world.find_path("room1", "nonexistent")

    assert path is None


def test_world_find_path_blocked_by_lock():
    """Test finding path blocked by locked exit."""
    world = World()
    world.add("room1", "Room 1")
    world.add("room2", "Room 2")
    world.connect("room1", "north", "room2", locked=True)

    path = world.find_path("room1", "room2")

    assert path is None


def test_world_to_dict():
    """Test world serialization to dict."""
    world = World(title="Test World")
    world.add("room1", "Room 1", "Description 1")
    world.add("room2", "Room 2", "Description 2")
    world.connect("room1", "north", "room2", description="A door")

    data = world.to_dict()

    assert data["title"] == "Test World"
    assert len(data["rooms"]) == 2

    room1_data = next(r for r in data["rooms"] if r["id"] == "room1")
    assert room1_data["name"] == "Room 1"
    assert room1_data["description"] == "Description 1"
    assert "north" in room1_data["exits"]
    assert room1_data["exits"]["north"]["to"] == "room2"
    assert room1_data["exits"]["north"]["description"] == "A door"


def test_world_from_dict():
    """Test world deserialization from dict."""
    data = {
        "title": "Test World",
        "rooms": [
            {
                "id": "room1",
                "name": "Room 1",
                "description": "Description 1",
                "exits": {
                    "north": {"to": "room2", "description": "A door", "locked": False}
                },
            },
            {
                "id": "room2",
                "name": "Room 2",
                "description": "Description 2",
                "exits": {},
            },
        ],
    }

    world = World.from_dict(data)

    assert world.title == "Test World"
    assert world.has_room("room1")
    assert world.has_room("room2")

    room1 = world.require_room("room1")
    assert room1.name == "Room 1"
    assert room1.description == "Description 1"
    assert "north" in room1.exits
    assert room1.exits["north"].to_room == "room2"
    assert room1.exits["north"].description == "A door"


def test_world_serialization_roundtrip():
    """Test world serialization roundtrip."""
    world = World(title="Test World")
    world.add("room1", "Room 1", "Description 1")
    world.add("room2", "Room 2", "Description 2")
    world.connect("room1", "north", "room2", locked=True)

    data = world.to_dict()
    world2 = World.from_dict(data)

    assert world2.title == world.title
    assert set(r.id for r in world2.rooms()) == set(r.id for r in world.rooms())

    # Test that locked exit is preserved
    room1 = world2.require_room("room1")
    assert room1.exits["north"].locked is True


def test_load_default_world():
    """Test loading the default world."""
    world = load_default_world()

    assert world.title == "DiceRealms – Beginner's Vale"
    assert world.has_room("town_square")
    assert world.has_room("tavern")
    assert world.has_room("market")
    assert world.has_room("north_road")
    assert world.has_room("gate")

    # Test some connections
    assert "south" in world.neighbors("town_square")
    assert world.neighbors("town_square")["south"] == "tavern"

    # Test locked exit
    assert "north" not in world.neighbors("north_road")
    north_road = world.require_room("north_road")
    assert north_road.exits["north"].locked is True


def test_load_default_world_connections():
    """Test that default world has correct connections."""
    world = load_default_world()

    # Test bidirectional connections
    assert world.neighbors("town_square")["south"] == "tavern"
    assert world.neighbors("tavern")["north"] == "town_square"
    assert world.neighbors("tavern")["east"] == "market"
    assert world.neighbors("market")["west"] == "tavern"
    assert world.neighbors("town_square")["north"] == "north_road"
    assert world.neighbors("north_road")["south"] == "town_square"

    # Test locked connection (one-way)
    assert "north" not in world.neighbors("north_road")
    north_road = world.require_room("north_road")
    assert north_road.exits["north"].to_room == "gate"
    assert north_road.exits["north"].locked is True
