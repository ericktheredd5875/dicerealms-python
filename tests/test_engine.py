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
        assert "unknown command" in result.lower()

    def test_empty_input(self, engine):
        assert engine.handle("") == ""

    def test_help_lists_commands(self, engine):
        result = engine.handle("help")
        assert "roll" in result
        assert "look" in result
        assert "move" in result
        assert "quit" in result

    def test_roll_valid(self, engine):
        result = engine.handle("roll 2d6")
        assert "->" in result

    def test_roll_no_args(self, engine):
        result = engine.handle("roll")
        assert "usage" in result.lower()

    def test_roll_invalid_expr(self, engine):
        result = engine.handle("roll notdice")
        assert "error" in result.lower()

    def test_quit_returns_sentinel(self, engine):
        assert engine.handle("quit") == "__QUIT__"

    def test_look_fallback_without_world(self, engine):
        result = engine.handle("look")
        assert len(result) > 0  # Returns something

    def test_look_with_world(self, full_engine):
        # starts in town_square
        result = full_engine.handle("look")  
        assert "Town Square" in result
        assert "Exits" in result

    def test_move_no_args(self, full_engine):
        result = full_engine.handle("move")
        assert "usage" in result.lower()

    def test_move_valid_direction(self, full_engine):
        result = full_engine.handle("move south")
        assert "Tavern" in result

    def test_move_invalid_direction(self, full_engine):
        result = full_engine.handle("move east")
        assert "can't go" in result.lower()

    def test_move_updates_player_room(self, full_engine):
        full_engine.handle("move south")
        result = full_engine.handle("look")
        assert "Tavern" in result