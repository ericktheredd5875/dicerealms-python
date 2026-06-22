# dicerealms/protocol/messages.py
"""
Message protocol for DiceRealms multiplayer.
All messages are JSON-encoded WebSocket frames.
"""

from typing import Literal, NotRequired, TypedDict


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
    target: NotRequired[str | None]  # For whispers


# Server -> Client Messages
class ConnectedMessage(TypedDict):
    type: Literal["connected"]
    player_name: str
    message: str


class PlayerJoinedMessage(TypedDict):
    type: Literal["player_joined"]
    player: str


class PlayerLeftMessage(TypedDict):
    type: Literal["player_left"]
    player: str


class ErrorMessage(TypedDict):
    type: Literal["error"]
    message: str


class ChatBroadcastMessage(TypedDict):
    type: Literal["chat"]
    player: str
    message: str


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
    current_player_id: str | None
    is_your_turn: bool
    waiting_for: str | None
    queue_position: int
    queue_size: int


ServerMessage = {
    WelcomeMessage
    | ConnectedMessage
    | PlayerJoinedMessage
    | PlayerLeftMessage
    | ErrorMessage
    | ChatBroadcastMessage
    | ActionAnnouncementMessage
    | ActionResultMessage
    | TurnStatusMessage
}

