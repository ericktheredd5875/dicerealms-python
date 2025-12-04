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

        # Validate turn
        if not self.turn_manager.is_current_turn(player_id):
            return {
                "success": False,
                "error": f"Not your turn! Current player: {self.turn_manager.get_current_player()}",
            }

        # Start turn action
        if not self.turn_manager.start_turn_action(player_id):
            return {
                "success": False,
                "error": "Cannot start action: turn action already in progress.",
            }

        try:
            # 1. Broadcast action announcement
            await self.broadcast({
                "type": "action_announcement",
                "player": player.name,
                "action": action,
                "args": " ".join(args),
                "status": "starting",
            })

            # 2. Wait for dramatic effect
            await asyncio.sleep(self.action_delay)

            # 3. Execute action
            result_dict = {"success": True}
            
            if action == "roll":
                # Handle dice rolling
                if not args:
                    result_dict = {
                        "success": False,
                        "error": "Roll action requires dice expression (e.g., '2d6').",
                    }
                else:
                    dice_expr = args[0]
                    try:
                        total, parts = roll_dice(dice_expr)
                        result_dict = {
                            "success": True,
                            "result": f"{player.name} rolled {dice_expr}: {total} (Parts: {parts})",
                            "details": {
                                "dice": dice_expr,
                                "total": total,
                                "parts": parts,
                            },
                        }
                    except ValueError as e:
                        result_dict = {
                            "success": False,
                            "error": f"Invalid dice expression: {e}",
                        }
            elif action == "move":
                # Handle movement
                if not args:
                    result_dict = {
                        "success": False,
                        "error": "Move action requires direction (e.g., 'north', 'south').",
                    }
                else:
                    direction = args[0]
                    success, message = self.game_state.move_player(player_id, direction)
                    result_dict = {
                        "success": success,
                        "result": message,
                        "details": {
                            "direction": direction,
                            "new_room": self.game_state.get_player(player_id).room if success else None,
                        },
                    }
            else:
                # Unknown action
                result_dict = {
                    "success": False,
                    "error": f"Unknown action: {action}",
                }

            # 4. Broadcast action result
            await self.broadcast({
                "type": "action_result",
                "player": player.name,
                "action": action,
                "result": result_dict.get("result", result_dict.get("error", "Action completed")),
                "details": result_dict.get("details", {}),
            })

            # 5. End turn action
            self.turn_manager.end_turn_action()

            # 6. Advance turn
            self.turn_manager.advance_turn()

            return result_dict

        except Exception as e:
            # Ensure we end the turn action even on error
            self.turn_manager.end_turn_action()
            logger.error(f"Error processing action for {player_id}: {e}")
            return {
                "success": False,
                "error": f"Error processing action: {e}",
            }
        
        
