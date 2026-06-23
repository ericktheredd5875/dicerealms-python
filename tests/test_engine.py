# SPDX-License-Identifier: MIT
"""Tests for GameEngine command handling."""
import pytest

from dicerealms.engine import GameEngine
from dicerealms.player import Player
from dicerealms.world import load_default_world


@pytest.fixture
def engine():
    """Engine without world — tests fallback behavior."""
    return GameEngine()


@pytest.fixture
def full_engine():
    """Engine with world and player wired in."""
    world = load_default_world()
    player = Player()
    return GameEngine(world=world, player=player)


class TestGameEngine:

    def test_unknown_command(self, engine):
        result = engine.handle("fly")
        assert result["type"] == "error"
        assert "unknown command" in result["message"].lower()

    def test_empty_input(self, engine):
        result = engine.handle("")
        assert result["type"] == "empty"

    def test_help_lists_commands(self, engine):
        result = engine.handle("help")
        assert result["type"] == "help"
        names = [c["name"] for c in result["commands"]]
        assert "roll" in names
        assert "look" in names
        assert "move" in names
        assert "quit" in names

    def test_roll_valid(self, engine):
        result = engine.handle("roll 2d6")
        assert result["type"] == "roll"
        assert "total" in result
        assert "parts" in result

    def test_roll_no_args(self, engine):
        result = engine.handle("roll")
        assert result["type"] == "error"
        assert "usage" in result["message"].lower()

    def test_roll_invalid_expr(self, engine):
        result = engine.handle("roll notdice")
        assert result["type"] == "error"

    def test_quit_returns_sentinel(self, engine):
        result = engine.handle("quit")
        assert result["type"] == "quit"

    def test_look_fallback_without_world(self, engine):
        result = engine.handle("look")
        assert result["type"] == "look"
        assert len(result["description"]) > 0

    def test_look_with_world(self, full_engine):
        result = full_engine.handle("look")
        assert result["type"] == "look"
        assert "Town Square" in result["room"]
        assert len(result["exits"]) > 0

    def test_move_no_args(self, full_engine):
        result = full_engine.handle("move")
        assert result["type"] == "error"
        assert "usage" in result["message"].lower()

    def test_move_valid_direction(self, full_engine):
        result = full_engine.handle("move south")
        assert result["type"] == "move"
        assert "Tavern" in result["room"]

    def test_move_invalid_direction(self, full_engine):
        result = full_engine.handle("move east")
        assert result["type"] == "error"
        assert "can't go" in result["message"].lower()

    def test_move_updates_player_room(self, full_engine):
        full_engine.handle("move south")
        result = full_engine.handle("look")
        assert "Tavern" in result["room"]

    def test_stats_no_player(self, engine):
        result = engine.handle("stats")
        assert result["type"] == "error"
        assert "no player" in result["message"].lower()

    def test_stats_shows_defaults(self, full_engine):
        result = full_engine.handle("stats")
        assert result["type"] == "stats"
        assert result["hp"] == 20
        assert result["max_hp"] == 20
        assert result["mp"] == 10
        assert result["max_mp"] == 10

    def test_stats_shows_player_name(self, full_engine):
        result = full_engine.handle("stats")
        assert result["name"] == full_engine._player.name

    def test_help_includes_stats(self, engine):
        result = engine.handle("help")
        names = [c["name"] for c in result["commands"]]
        assert "stats" in names
