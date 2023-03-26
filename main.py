import socket
import logging

from client.session import Session
from client.actions import *
from client.responses import *
from player.player import Player
from player.engine import Bot


logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s",
    level=logging.DEBUG)


def handle_response(resp):
    match resp:
        case ErrorResponse(_, error_message):
            raise RuntimeError(f"Server error: {error_message}")
        case _:
            return resp


if __name__ == "__main__":
    with Session("wgforge-srv.wargaming.net", 443) as s:
        player_info = s.login(LoginAction("yagde-test-user"))
        player_bot = Bot(s, player_info)
        handle_response(player_info)

        player_bot.bot_engine()
        
        handle_response(s.logout())
