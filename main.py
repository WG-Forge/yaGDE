import socket
import json
import struct

from client.session import Session
from client.actions import *
from client.responses import *


def handle_response(resp):
    match resp:
        case ErrorResponse(_, error_message):
            raise RuntimeError(f"Server error: {error_message}")
        case _:
            return resp


if __name__ == "__main__":
    with Session("wgforge-srv.wargaming.net", 443) as s:
        handle_response(s.login(LoginAction("yagde-test-user")))
        while True:
            game_state = handle_response(s.game_state())
            if game_state.current_turn == game_state.num_turns:
                break
            game_map = handle_response(s.map())
            game_actions = handle_response(s.game_actions())
            print(game_state.current_turn, game_map)
            handle_response(s.turn())
        handle_response(s.logout())
