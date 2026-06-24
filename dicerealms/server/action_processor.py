"""
Action processor for DiceRealms.
Handles synchronized turn-based actions with announcement -> Wait -> Execution -> Result flow.
"""

import asyncio
from collections.abc import Awaitable, Callable

from loguru import logger

from dicerealms.commands import COMMANDS, FREE_ACTIONS
from dicerealms.core import roll_dice
from dicerealms.protocol.messages import (
    ActionAnnouncementMessage,
    ActionResultMessage,
    ErrorMessage,
)
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
        self.action_delay = 2.0

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

        # FREE actions: skip turn validation, delay, and turn advance
        if action.lower() in FREE_ACTIONS:
            try:
                result = await self._execute_action(player_id, action, args)
                action_result: ActionResultMessage = {
                    "type": "action_result",
                    "player": player_name,
                    "action": action,
                    "result": result.get("result", ""),
                    "details": result.get("details", {})
                }
                await self.broadcast(action_result)
                return {"success": True, "result": result}
            except Exception as e:
                logger.error(f"FREE action error for {player_id}: {e}")
                return {"success": False, "error": str(e)}

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

        succeeded = False
        try:
            # 1. Broadcast action announcement
            announcement: ActionAnnouncementMessage = {
                "type": "action_announcement",
                "player": player.name,
                "action": action,
                "args": " ".join(args),
                "status": "starting",
            }
            await self.broadcast(announcement)
            logger.info(f"Action announcement: {player_name} is {action}ing {args}")

            # 2. Wait for dramatic effect
            await asyncio.sleep(self.action_delay)
            logger.info(f"Action wait: {player_name} waited for {self.action_delay} seconds")

            # 3. Execute action
            result = await self._execute_action(player_id, action, args)
            logger.info(f"Action result: {result}")

            # 4. Broadcast action result
            action_result: ActionResultMessage = {
                "type": "action_result",
                "player": player.name,
                "action": action,
                "result": result.get("result", 
                        result.get("error", "Action completed")),
                "details": result.get("details", {}),
            }
            await self.broadcast(action_result)
            logger.info(f"Action result broadcast: {player_name} - {action}")

            succeeded = True
            return {
                "success": True,
                "result": result
            }

        except Exception as e:
            err: ErrorMessage = {
                "type": "error",
                "message": f"Error processing {action}: {str(e)}",
            }
            logger.error(f"Error processing action for {player_id}: {e}")
            await self.broadcast(err)
            return {
                "success": False,
                "error":str(e),
            }

        finally:
            # 5. End turn action, then advance, ALWAYS
            self.turn_manager.end_turn_action()
            if succeeded:
                self.turn_manager.advance_turn()


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
        elif action_lower == "stats":
            return await self._execute_stats(player_id)
        elif action_lower == "who":
            return await self._execute_who()
        elif action_lower == "inspect":
            return await self._execute_inspect(args)
        elif action_lower == "help":
            return await self._execute_help()
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
            raise ValueError(f"Invalid dice expression: {dice_expr} - {(e)}") from e


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

            room_description = room.description if room else "Unknown room"
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
                "other_players": [p.name for p in players_in_room],
            },
        }
        

    async def _execute_stats(self, player_id: str) -> dict:
        player = self.game_state.get_player(player_id)
        if not player:
            raise ValueError(f"Player not found. {player_id}")
        
        result = (
            f"Name: {player.name}\n"
            f"Level: {player.level} XP: {player.xp}\n"
            f"HP: {player.hp}/{player.max_hp}\n"
            f"MP: {player.mp}/{player.max_mp}"
        )

        return {
            "result": result,
            "details": {
                "name": player.name,
                "level": player.level,
                "xp": player.xp,
                "hp": player.hp,
                "max_hp": player.max_hp,
                "mp": player.mp,
                "max_mp": player.max_mp,
            }
        }


    async def _execute_who(self) -> dict:
        players = [
            {"name": p.name, "room": p.room}
            for p in self.game_state.players.values()
        ]
        result = "Players in game:\n" + "\n".join(
            f"  {p['name']} ({p['room']})" for p in players
        )
        return {"result": result, "details": {"players": players}}


    async def _execute_inspect(self, args: list[str]) -> dict:
        if not args:
            raise ValueError("Usage: inspect <player_name>")
        
        target_name = args[0]
        target = next(
            (p for p in self.game_state.players.values()
            if p.name.lower() == target_name.lower()),
            None,
        )
        if not target:
            raise ValueError(f"Player '{target_name}' not found.")
        
        result = (
            f"[{target_name}]\n"
            f"Level: {target.level}  "
            f"HP: {target.hp}/{target.max_hp}  "
            f"MP: {target.mp}/{target.max_mp}"
        )
        return {
            "result": result,
            "details": {
                "name": target.name,
                "level": target.level,
                "hp": target.hp,
                "max_hp": target.max_hp,
                "mp": target.mp,
                "max_mp": target.max_mp,
            }
        }


    async def _execute_help(self) -> dict:
        """
        Execute the view of the help menu.
        """
        actions = [(c.name, c.help) for c in COMMANDS]

        result = "Available actions:\n" + "\n".join(f"{name:<8} {desc}" for name, desc in actions)
        return {
            "result": result,
            "details": {
                "actions": [name for name, _ in actions],
            }
        }