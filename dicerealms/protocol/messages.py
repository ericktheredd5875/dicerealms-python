# dicerealms/protocol/messages.py
"""
Message protocol for DiceRealms multiplayer.
All messages are JSON-encoded WebSocket frames.
"""

from typing import Literal, Optional, TypedDict


# Client -> Server Messages
class ConnectMessage(TypedDict):
    type: Literal["connect"]
    player_name: str

class ActionMessage(TypedDict):
    type: Literal["action"]
    action: str  # "roll", "move", "look", etc.
    args: list[str]

class ChatMessage(TypedDict):
    type: Literal["chat"]
    message: str
    target: Optional[str] | None = None  # For whispers

# Server -> Client Messages
class WelcomeMessage(TypedDict):
    type: Literal["welcome"]
    player_id: str
    message: str

class ActionAnnouncementMessage(TypedDict):
    type: Literal["action_announcement"]
    player: str
    action: str
    args: str
    status: Literal["starting"]

class ActionResultMessage(TypedDict):
    type: Literal["action_result"]
    player: str
    action: str
    result: str
    details: dict  # Action-specific details

class TurnStatusMessage(TypedDict):
    type: Literal["turn_status"]
    current_player: str
    is_your_turn: bool
    waiting_for: Optional[str]

