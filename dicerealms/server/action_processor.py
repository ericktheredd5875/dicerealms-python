"""
Action processor for DiceRealms.
Handles synchronized turn-based actions with announcement -> Wait -> Execution -> Result flow.
"""

import asyncio
from collections.abc import Awaitable
from typing import Callable, Optional

from loguru import logger

from dicerealms.core import roll_dice
from dicerealms.server.game_state import GameState
from dicerealms.server.turn_manager import TurnManager


class ActionProcessor:
    """
    Processes game actions with synchronized turn-based execution.
    Implements: announcement -> Wait -> Execution -> Result broadcasting.
    """

    def __init__(self, game_state: GameState, turn_manager: TurnManager, broadcast_callback: Callable[[dict], Awaitable[None]]):
        """
        Initialize the Action Processor.

        Args:
        - game_state: the shared game state.
        - turn_manager: the turn management system.
        - broadcast_callback: Async function to broadcast messages to all clients.
        """
        self.game_state = game_state
        self.turn_manager = turn_manager
        self.broadcast = broadcast_callback
        self.action_delay = 2.0 # * Seconds to wait for dramatic effect.

    async def process_action(self, player_id: str, action: str, args: list[str]) -> dict:
        """
        Process a game action with full synchronized flow.

        Flow:
        1. Validate turn.
        2. Broadcast action announcement.
        3. Wait (synchronized delay).
        4. Execute action.
        5. Broadcast action result.
        6. Advance turn.
        
        Returns:
            dict with result information or error message.
        """

        # Get player info
        player = self.game_state.get_player(player_id)
        if not player:
            return {
                "success": False,
                "error": "Player not found in game state.",
            }

        
