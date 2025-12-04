# SPDX-License-Identifier: MIT
"""Tests for ActionProcessor class."""

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from dicerealms.server.action_processor import ActionProcessor
from dicerealms.server.game_state import GameState
from dicerealms.server.turn_manager import TurnManager


@pytest.fixture
def game_state():
    """Create a GameState instance for testing."""
    return GameState()


@pytest.fixture
def turn_manager():
    """Create a TurnManager instance for testing."""
    return TurnManager()


@pytest.fixture
def broadcast_callback():
    """Create a mock broadcast callback."""
    return AsyncMock()


@pytest.fixture
def action_processor(game_state, turn_manager, broadcast_callback):
    """Create an ActionProcessor instance for testing."""
    return ActionProcessor(game_state, turn_manager, broadcast_callback)


class TestActionProcessor:
    """Test suite for ActionProcessor."""

    def test_initialization(self, action_processor, game_state, turn_manager):
        """Test ActionProcessor initializes correctly."""
        assert action_processor.game_state == game_state
        assert action_processor.turn_manager == turn_manager
        assert action_processor.action_delay == 2.0

    @pytest.mark.asyncio
    async def test_process_action_player_not_found(self, action_processor):
        """Test processing action for non-existent player."""
        result = await action_processor.process_action("nonexistent", "roll", ["1d6"])
        
        assert result["success"] is False
        assert "not found" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_process_action_not_current_turn(self, action_processor, game_state, turn_manager):
        """Test processing action when it's not player's turn."""
        player_id = "player_1"
        other_player = "player_2"
        
        game_state.add_player(player_id, "Alice")
        turn_manager.add_player(other_player)
        turn_manager.add_player(player_id)
        
        result = await action_processor.process_action(player_id, "roll", ["1d6"])
        print(result)
        
        assert result["success"] is False
        assert "not your turn" in result["error"].lower()

    @pytest.mark.asyncio
    async def test_process_action_roll_dice(self, action_processor, game_state, turn_manager, broadcast_callback):
        """Test processing a roll dice action."""
        player_id = "player_1"
        other_player = "player_2"
        
        game_state.add_player(player_id, "Alice")
        game_state.add_player(other_player, "Bob")
        turn_manager.add_player(player_id)
        turn_manager.add_player(other_player)
        
        result = await action_processor.process_action(player_id, "roll", ["2d6"])
        
        # Should broadcast action announcement and result
        assert broadcast_callback.call_count >= 2
        
        # Check that turn was advanced to the next player
        assert turn_manager.get_current_player() == other_player

    @pytest.mark.asyncio
    async def test_process_action_delay(self, action_processor, game_state, turn_manager, broadcast_callback):
        """Test that action processing includes delay."""
        player_id = "player_1"
        game_state.add_player(player_id, "Alice")
        turn_manager.add_player(player_id)
        
        start_time = asyncio.get_event_loop().time()
        await action_processor.process_action(player_id, "roll", ["1d6"])
        end_time = asyncio.get_event_loop().time()
        
        # Should take at least action_delay seconds
        elapsed = end_time - start_time
        assert elapsed >= action_processor.action_delay