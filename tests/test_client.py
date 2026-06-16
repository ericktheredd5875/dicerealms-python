
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import websockets

from dicerealms.client.client import GameClient
from dicerealms.client.ui import ClientUI


class FakeWebSocket:
    def __init__(self, messages: list[str]):
        self._messages = messages
        self.sent: list[str] = []

    
    def __aiter__(self):
        return self._iter()
    

    async def _iter(self):
        for msg in self._messages:
            yield msg

    
    async def send(self, data: str):
        self.sent.append(data)


    async def close(self):
        pass


@pytest.fixture
def send_callback():
    return AsyncMock()

@pytest.mark.parametrize("msg_type,handler", [
    ("welcome", "display_welcome"),
    ("connected", "display_connected"),
    ("player_joined", "display_player_joined"),
    ("player_left", "display_player_left"),
    ("chat", "display_chat"),
    ("action_announcement", "display_action_announcement"),
    ("action_result", "display_action_result"),
    ("turn_status", "display_turn_status"),
    ("error", "display_error"),
])
def test_display_dispatches_to_handler(msg_type, handler):
    ui = ClientUI()
    with patch.object(ui, handler) as mock:
        ui.display({"type": msg_type})
        mock.assert_called_once()


def test_display_unknown_type_no_crash():
    ui = ClientUI()
    ui.display({"type": "unknown_xyz"}) # should not raise


async def test_send_message_not_connected_raises():
    client = GameClient("ws://localhost:8765", "Alice")
    with pytest.raises(RuntimeError):
        await client.send_message({"type": "test"})

async def test_send_message_serializes_json():
    client = GameClient("ws://localhost:8765", "Alice")
    client._ws = FakeWebSocket([])
    await client.send_message({"type": "chat", "message": "hi"})
    assert client._ws.sent == ['{"type": "chat", "message": "hi"}']

async def test_receive_loop_dispatches_to_ui():
    client = GameClient("ws://localhost:8765", "Alice")
    client.ui = MagicMock()
    msg = {"type": "welcome", "player_id": "p1", "message": "Welcome!"}
    client._ws = FakeWebSocket([json.dumps(msg)])
    await client._receive_loop()
    client.ui.display.assert_called_once_with(msg)

async def test_receive_loop_handles_connection_closed():
    client = GameClient("ws://localhost:8765", "Alice")
    client.ui = MagicMock()

    class ClosingWS:
        def __aiter__(self): return self
        async def __anext__(self):
            raise websockets.exceptions.ConnectionClosed(None, None)

    client._ws = ClosingWS()
    await client._receive_loop()  # should not raise
    assert client.connected is False


async def test_connect_sends_connect_message():
    client = GameClient("ws://localhost:8765", "Alice")
    fake_ws = FakeWebSocket([])
    with patch("dicerealms.client.client.websockets.connect", new_callable=AsyncMock, return_value=fake_ws):
        await client.connect()
    assert client.connected is True
    sent = json.loads(fake_ws.sent[0])
    assert sent["type"] == "connect"
    assert sent["player_name"] == "Alice"