"""M3 multiplayer integration tests — two clients, full message flow."""
import json
from unittest.mock import AsyncMock

import pytest
from websockets import ServerConnection

from dicerealms.server.server import GameServer


def get_messages(ws) -> list[dict]:
    return [json.loads(call[0][0]) for call in ws.send.call_args_list]


@pytest.fixture
async def two_player_server():
    server = GameServer()
    server.action_processor.action_delay = 0  # no delay in tests

    ws1 = AsyncMock(spec=ServerConnection)
    ws2 = AsyncMock(spec=ServerConnection)

    p1_id = "player_1"
    server.connected_clients[p1_id] = ws1
    server.turn_manager.add_player(p1_id)
    await server.send_to_client(p1_id, {"type": "welcome", "player_id": p1_id, "message": "Welcome!"})
    await server.handle_connect(p1_id, {"type": "connect", "player_name": "Alice"})

    p2_id = "player_2"
    server.connected_clients[p2_id] = ws2
    server.turn_manager.add_player(p2_id)
    await server.send_to_client(p2_id, {"type": "welcome", "player_id": p2_id, "message": "Welcome!"})
    await server.handle_connect(p2_id, {"type": "connect", "player_name": "Bob"})

    return server, p1_id, p2_id, ws1, ws2


class TestTwoPlayerFlow:

    async def test_both_players_get_welcome(self, two_player_server):
        _, p1_id, p2_id, ws1, ws2 = two_player_server
        assert any(m["type"] == "welcome" for m in get_messages(ws1))
        assert any(m["type"] == "welcome" for m in get_messages(ws2))

    async def test_player_joined_broadcast_to_existing_players(self, two_player_server):
        _, p1_id, p2_id, ws1, ws2 = two_player_server
        # Alice should have seen Bob join
        joined = [m for m in get_messages(ws1) if m["type"] == "player_joined"]
        assert any(m["player"] == "Bob" for m in joined)

    async def test_action_announcement_reaches_both_players(self, two_player_server):
        server, p1_id, p2_id, ws1, ws2 = two_player_server
        ws1.send.reset_mock()
        ws2.send.reset_mock()

        await server.handle_action(p1_id, {"type": "action", "action": "roll", "args": ["1d6"]})

        assert any(m["type"] == "action_announcement" for m in get_messages(ws1))
        assert any(m["type"] == "action_announcement" for m in get_messages(ws2))

    async def test_action_result_reaches_both_players(self, two_player_server):
        server, p1_id, p2_id, ws1, ws2 = two_player_server
        ws1.send.reset_mock()
        ws2.send.reset_mock()

        await server.handle_action(p1_id, {"type": "action", "action": "roll", "args": ["1d6"]})

        assert any(m["type"] == "action_result" for m in get_messages(ws1))
        assert any(m["type"] == "action_result" for m in get_messages(ws2))

    async def test_announcement_arrives_before_result(self, two_player_server):
        server, p1_id, p2_id, ws1, ws2 = two_player_server
        ws2.send.reset_mock()

        await server.handle_action(p1_id, {"type": "action", "action": "roll", "args": ["1d6"]})

        types = [m["type"] for m in get_messages(ws2)]
        assert types.index("action_announcement") < types.index("action_result")

    async def test_turn_advances_after_action(self, two_player_server):
        server, p1_id, p2_id, ws1, ws2 = two_player_server

        await server.handle_action(p1_id, {"type": "action", "action": "roll", "args": ["1d6"]})

        assert server.turn_manager.get_current_player() == p2_id

    async def test_out_of_turn_action_rejected(self, two_player_server):
        server, p1_id, p2_id, ws1, ws2 = two_player_server
        ws2.send.reset_mock()

        # Bob tries to act when it's Alice's turn
        await server.handle_action(p2_id, {"type": "action", "action": "roll", "args": ["1d6"]})

        msgs = get_messages(ws2)
        assert any(m["type"] == "error" and "not your turn" in m["message"].lower() for m in msgs)

    async def test_chat_reaches_all_players(self, two_player_server):
        server, p1_id, p2_id, ws1, ws2 = two_player_server
        ws1.send.reset_mock()
        ws2.send.reset_mock()

        await server.handle_chat(p1_id, {"type": "chat", "message": "Hello!"})

        assert any(m["type"] == "chat" and m["message"] == "Hello!" for m in get_messages(ws1))
        assert any(m["type"] == "chat" and m["message"] == "Hello!" for m in get_messages(ws2))

    async def test_turn_status_sent_after_action(self, two_player_server):
        server, p1_id, p2_id, ws1, ws2 = two_player_server
        ws1.send.reset_mock()
        ws2.send.reset_mock()

        await server.handle_action(p1_id, {"type": "action", "action": "roll", "args": ["1d6"]})

        assert any(m["type"] == "turn_status" for m in get_messages(ws1))
        assert any(m["type"] == "turn_status" for m in get_messages(ws2))
