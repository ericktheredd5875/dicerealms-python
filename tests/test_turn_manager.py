# SPDX-License-Identifier: MIT
"""Tests for TurnManager class."""

import pytest

from dicerealms.server.turn_manager import TurnManager


class TestTurnManager:
    """Test suite for TurnManager."""

    def test_initialization(self):
        """Test TurnManager initializes with empty queue."""
        tm = TurnManager()
        assert tm.turn_queue == []
        assert tm.current_turn_index == 0
        assert tm.turn_in_progress is False

    def test_add_player(self):
        """Test adding players to turn queue."""
        tm = TurnManager()
        assert tm.add_player("player_1") is True
        assert "player_1" in tm.turn_queue
        assert tm.get_current_player() == "player_1"

    def test_add_multiple_players(self):
        """Test adding multiple players maintains order."""
        tm = TurnManager()
        tm.add_player("player_1")
        tm.add_player("player_2")
        tm.add_player("player_3")
        
        assert tm.turn_queue == ["player_1", "player_2", "player_3"]
        assert tm.get_current_player() == "player_1"

    def test_add_duplicate_player(self):
        """Test adding duplicate player returns False."""
        tm = TurnManager()
        tm.add_player("player_1")
        assert tm.add_player("player_1") is False

    def test_remove_player(self):
        """Test removing a player from queue."""
        tm = TurnManager()
        tm.add_player("player_1")
        tm.add_player("player_2")
        
        assert tm.remove_player("player_1") is True
        assert "player_1" not in tm.turn_queue
        assert tm.get_current_player() == "player_2"

    def test_remove_current_player(self):
        """Test removing current player advances to next."""
        tm = TurnManager()
        tm.add_player("player_1")
        tm.add_player("player_2")
        tm.add_player("player_3")
        
        assert tm.get_current_player() == "player_1"
        tm.remove_player("player_1")
        assert tm.get_current_player() == "player_2"

    def test_remove_player_before_current(self):
        """Test removing player before current adjusts index."""
        tm = TurnManager()
        tm.add_player("player_1")
        tm.add_player("player_2")
        tm.add_player("player_3")
        
        # Set current to player_2
        tm.current_turn_index = 1
        assert tm.get_current_player() == "player_2"
        
        # Remove player_1 (before current)
        tm.remove_player("player_1")
        assert tm.current_turn_index == 0
        assert tm.get_current_player() == "player_2"

    def test_remove_nonexistent_player(self):
        """Test removing non-existent player returns False."""
        tm = TurnManager()
        assert tm.remove_player("nonexistent") is False

    def test_get_current_player_empty_queue(self):
        """Test get_current_player returns None for empty queue."""
        tm = TurnManager()
        assert tm.get_current_player() is None

    def test_is_current_turn(self):
        """Test is_current_turn correctly identifies current player."""
        tm = TurnManager()
        tm.add_player("player_1")
        tm.add_player("player_2")
        
        assert tm.is_current_turn("player_1") is True
        assert tm.is_current_turn("player_2") is False

    def test_is_current_turn_when_action_in_progress(self):
        """Test is_current_turn returns False when action in progress."""
        tm = TurnManager()
        tm.add_player("player_1")
        tm.turn_in_progress = True
        
        assert tm.is_current_turn("player_1") is False

    def test_start_turn_action(self):
        """Test starting a turn action."""
        tm = TurnManager()
        tm.add_player("player_1")
        
        assert tm.start_turn_action("player_1") is True
        assert tm.turn_in_progress is True

    def test_start_turn_action_wrong_player(self):
        """Test starting action for wrong player returns False."""
        tm = TurnManager()
        tm.add_player("player_1")
        tm.add_player("player_2")
        
        assert tm.start_turn_action("player_2") is False
        assert tm.turn_in_progress is False

    def test_start_turn_action_when_in_progress(self):
        """Test starting action when already in progress returns False."""
        tm = TurnManager()
        tm.add_player("player_1")
        tm.turn_in_progress = True
        
        assert tm.start_turn_action("player_1") is False

    def test_end_turn_action(self):
        """Test ending a turn action."""
        tm = TurnManager()
        tm.turn_in_progress = True
        tm.end_turn_action()
        
        assert tm.turn_in_progress is False

    def test_advance_turn(self):
        """Test advancing to next player's turn."""
        tm = TurnManager()
        tm.add_player("player_1")
        tm.add_player("player_2")
        tm.add_player("player_3")
        
        assert tm.get_current_player() == "player_1"
        next_player = tm.advance_turn()
        assert next_player == "player_2"
        assert tm.get_current_player() == "player_2"

    def test_advance_turn_wraps_around(self):
        """Test turn advancement wraps around to first player."""
        tm = TurnManager()
        tm.add_player("player_1")
        tm.add_player("player_2")
        
        tm.advance_turn()
        assert tm.get_current_player() == "player_2"
        tm.advance_turn()
        assert tm.get_current_player() == "player_1"

    def test_advance_turn_when_in_progress(self):
        """Test cannot advance turn when action in progress."""
        tm = TurnManager()
        tm.add_player("player_1")
        tm.turn_in_progress = True
        
        assert tm.advance_turn() is None
        assert tm.get_current_player() == "player_1"

    def test_advance_turn_empty_queue(self):
        """Test cannot advance turn with empty queue."""
        tm = TurnManager()
        assert tm.advance_turn() is None

    def test_get_next_player(self):
        """Test getting next player without advancing."""
        tm = TurnManager()
        tm.add_player("player_1")
        tm.add_player("player_2")
        tm.add_player("player_3")
        
        assert tm.get_next_player() == "player_2"
        assert tm.get_current_player() == "player_1"  # Should not advance

    def test_get_next_player_wraps_around(self):
        """Test get_next_player wraps around."""
        tm = TurnManager()
        tm.add_player("player_1")
        tm.add_player("player_2")
        tm.current_turn_index = 1  # player_2's turn
        
        assert tm.get_next_player() == "player_1"

    def test_get_next_player_empty_queue(self):
        """Test get_next_player returns None for empty queue."""
        tm = TurnManager()
        assert tm.get_next_player() is None

    def test_get_turn_status(self):
        """Test getting turn status for a player."""
        tm = TurnManager()
        tm.add_player("player_1")
        tm.add_player("player_2")
        
        status = tm.get_turn_status("player_1")
        assert status["is_your_turn"] is True
        assert status["current_player"] == "player_1"
        assert status["queue_position"] == 0
        assert status["queue_size"] == 2
        assert status["turn_in_progress"] is False

    def test_get_turn_status_not_current(self):
        """Test turn status for non-current player."""
        tm = TurnManager()
        tm.add_player("player_1")
        tm.add_player("player_2")
        
        status = tm.get_turn_status("player_2")
        assert status["is_your_turn"] is False
        assert status["queue_position"] == 1

    def test_get_turn_queue(self):
        """Test getting copy of turn queue."""
        tm = TurnManager()
        tm.add_player("player_1")
        tm.add_player("player_2")
        
        queue = tm.get_turn_queue()
        assert queue == ["player_1", "player_2"]
        # Modifying returned queue should not affect internal queue
        queue.append("player_3")
        assert len(tm.turn_queue) == 2

    def test_reset_turn_queue(self):
        """Test resetting turn queue."""
        tm = TurnManager()
        tm.add_player("player_1")
        tm.add_player("player_2")
        tm.current_turn_index = 1
        tm.turn_in_progress = True
        
        tm.reset_turn_queue()
        assert tm.turn_queue == []
        assert tm.current_turn_index == 0
        assert tm.turn_in_progress is False