from dicerealms.server.turn_manager import TurnManager

tm = TurnManager()
tm.add_player("player_1")
tm.add_player("player_2")
tm.add_player("player_3")

assert tm.get_current_player() == "player_1"
assert tm.is_current_turn("player_1") == True
assert tm.is_current_turn("player_2") == False

tm.advance_turn()
assert tm.get_current_player() == "player_2"

tm.remove_player("player_2")
assert tm.get_current_player() == "player_3"