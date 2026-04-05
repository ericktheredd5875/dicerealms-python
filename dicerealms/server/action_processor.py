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

    def __init__(
        self, 
        game_state: GameState, 
        turn_manager: TurnManager, 
        broadcast_callback: Callable[[dict], Awaitable[None]]):
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

        player_name = player.name

        # Validate it is the player's turn
        if not self.turn_manager.is_current_turn(player_id):
            current_player = self.turn_manager.get_current_player()
            current_player_name = (
                self.game_state.get_player(current_player).name
                if current_player and self.game_state.get_player(current_player)
                else "Unknown"
            )

            return {
                "success": False,
                "error": f"Not your turn! Current player: {current_player_name}",
            }

        # Start turn action
        if not self.turn_manager.start_turn_action(player_id):
            return {
                "success": False,
                "error": "Turn action already in progress.",
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
            logger.info(f"Action announcement: {player_name} is {action}ing {args}")

            # 2. Wait for dramatic effect
            await asyncio.sleep(self.action_delay)
            logger.info(f"Action wait: {player_name} waited for {self.action_delay} seconds")

            # 3. Execute action
            result = await self._execute_action(player_id, action, args)
            logger.info(f"Action result: {result}")

            # 4. Broadcast action result
            await self.broadcast({
                "type": "action_result",
                "player": player.name,
                "action": action,
                "result": result.get("result", result.get("error", "Action completed")),
                "details": result.get("details", {}),
            })
            logger.info(f"Action result broadcast: {player_name} - {action}")

            # 5. End turn action
            next_player_id = self.turn_manager.advance_turn()
            next_player_name = "Unknown"
            if next_player_id:
                next_player = self.game_state.get_player(next_player_id)
                if next_player:
                    next_player_name = next_player.name

            await self._broadcast_turn_status(next_player_id, next_player_name)

            return {
                "success": True,
                "result": result
            }

        except Exception as e:
            logger.error(f"Error processing action for {player_id}: {e}")
            await self.broadcast({
                "type": "error",
                "message": f"Error processing {action}: {str(e)}",
            })
            return {
                "success": False,
                "error":str(e),
            }

        finally:
            # Always end the turn action
            self.turn_manager.end_turn_action()

    async def _execute_action(
        self,
        player_id: str,
        action: str,
        args: list[str]) -> dict:

        """
        Execute a specific game action.
        Return dict with 'result' (string) and 'details' (dict)
        """

        action_lower = action.lower()
        if action_lower == "roll":
            return await self._execute_roll(args)

        elif action_lower == "move":
            return await self._execute_move(player_id, args)

        elif action_lower == "look":
            return await self._execute_look(player_id)

        else:
            raise ValueError(f"Unknown action: {action}")

    async def _execute_roll(self, args: list[str]) -> dict:
        """
        Execute a dice roll action.
        """

        if not args:
            raise ValueError("Roll action requires a dice expression (IE: 2d6+1)")
        
        dice_expr = args[0]
        try:
            total, parts = roll_dice(dice_expr)
            return {
                "result": f"Rolled {dice_expr} -> {total} (Parts: {parts})",
                "details": {
                    "expression": dice_expr,
                    "total": total,
                    "parts": parts,
                },
            }
        except ValueError as e:
            raise ValueError(f"Invalid dice expression: {dice_expr} - {str(e)}")

    async def _execute_move(self, player_id: str, args: list[str]) -> dict:
        """
        Execute a move action.
        """
        if not args:
            raise ValueError("Move action requires a direction (IE: north, south, east, west)")

        direction = args[0].lower()
        success, message = self.game_state.move_player(player_id, direction)

        if success:
            player = self.game_state.get_player(player_id)
            room = self.game_state.get_room(player.room) if player else None

            room_description = room.description if room else "Unknowd room"
            exits = ",".join(room.exits.keys()) if room and room.exits else "No Exits"

            return {
                "result": message,
                "details": {
                    "room": player.room if player else "Unknown",
                    "description": room_description,
                    "exits": exits,
                },
            }
        else:
            raise ValueError(message)

    async def _execute_look(self, player_id: str) -> dict:
        """
        Execute a look action.
        """
        player = self.game_state.get_player(player_id)
        if not player:
            raise ValueError("Player not found.")

        room = self.game_state.get_room(player.room)
        if not room:
            raise ValueError(f"Room {player.room} not found.")

        # Get other players in the room
        players_in_room = self.game_state.get_players_in_room(player.room)
        other_players = [p.name for p in players_in_room if p.player_id != player_id]

        exits = ",".join(room.exits.keys()) if room and room.exits else "None"

        description = f"{room.description}\n"
        if other_players:
            description += f"Other players in the room: {', '.join(other_players)}\n"
        description += f"Exits: {exits}"

        return {
            "result": description,
            "details": {
                "room": player.room if player else "Unknown",
                "description": room.description if room else "Unknown",
                "exits": list(room.exits.keys()),
                "other_players": [p.name for p in players_in_room],,
            },
        }
        
    ### START HERE -->> _execute_help
