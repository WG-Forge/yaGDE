import logging

from client.session import Session
from client.actions import *
from client.responses import *
from player.player import Player
from player.engine import Bot
from model.hex import *
from model.map import Map
from graphics.window import Window

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
    window = Window(1080, 1080, "YAGDE")

    while True:
        window.draw(Map(10))
        window.update()

    with Session("wgforge-srv.wargaming.net", 443) as s:
        player_info = s.login(LoginAction("yagde-test-user1"))
        player_bot = Bot(s, player_info)
        handle_response(player_info)

        # busy wait for second player to join
        not_all_connected = True

        """
        while not_all_connected:
           game_status = s.game_state()
           if game_status.num_players >= 2:
               not_all_connected = False
        """
        player_bot.bot_engine()

        handle_response(s.logout())
