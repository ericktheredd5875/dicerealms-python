# SPDX-License-Identifier: MIT
# tests/test_world.py

import pytest

from dicerealms.world import Room, World, load_default_world


@pytest.fixture()
def world():
    return load_default_world()


def test_rooms_exist(world):
    ids = {r.id for r in world.rooms()}
    assert {"town_square", "tavern", "market", "north_road", "gate"} <= ids


def test_neighbors_exclude_locked(world):
    # north_road has a locked exit north->gate (no back edge)
    n = world.neighbors("north_road")
    assert "north" not in n  # locked exits are not listed
    assert n["south"] == "town_square"


def test_move_success_and_failure(world):
    # Start in town_square
    rid = "town_square"

    # Valid move south to tavern
    rid, msg = world.move(rid, "south")
    assert rid == "tavern"
    assert "move south" in msg and "Tavern" in msg

    # Invalid move west from tavern (no exit)
    nxt, msg = world.move(rid, "west")
    assert nxt is None
    assert "can't go west" in msg

    # Move back north to town_square then north to north_road
    rid, _ = world.move(rid, "north")
    assert rid == "town_square"

    rid, _ = world.move(rid, "north")
    assert rid == "north_road"

    # Locked move to gate
    nxt, msg = world.move(rid, "north")
    assert nxt is None
    assert "locked" in msg.lower()


def test_look_lists_exits(world):
    text = world.look("town_square")
    # Exits are sorted alphabetically -> 'Exits: north, south'
    assert "Town Square" in text
    assert "Exits: north, south" in text


def test_find_path_basic(world):
    # Simple path market -> north_road
    path = world.find_path("market", "north_road")
    assert path == ["market", "tavern", "town_square", "north_road"]


def test_find_path_blocked_by_lock(world):
    # There is no path to gate due to locked exit
    assert world.find_path("town_square", "gate") is None


def test_serialization_roundtrip_preserves_locked(world):
    data = world.to_dict()
    w2 = World.from_dict(data)

    # Structure preserved
    assert set(r.id for r in w2.rooms()) == set(r.id for r in world.rooms())

    # Locked exit stays locked (north_road -> gate)
    # neighbors() filters locked, so ensure it's missing, but raw exit should be locked
    nr = w2.require_room("north_road")
    assert "north" not in w2.neighbors("north_road")
    assert nr.exits["north"].locked is True


@pytest.mark.parametrize(
    "start, direction, expected",
    [
        ("town_square", "south", "tavern"),
        ("tavern", "east", "market"),
        ("market", "west", "tavern"),
        ("tavern", "north", "town_square"),
    ],
)
def test_parametrized_moves(world, start, direction, expected):
    rid, _ = world.move(start, direction)
    assert rid == expected
