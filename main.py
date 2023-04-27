import logging
from contextlib import ExitStack
import time
from threading import Thread

from client.session import Session
from client.actions import *
from client.responses import *
from player.player import Player
from player.engine import Bot
from model.hex import *
from model.game import Game
from graphics.window import Window

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s",
    level=logging.DEBUG)


class TasksGroup:
    # This is a hack to make turns work because they are blocking

    def __init__(self):
        self._tasks = []

    def add(self, task, args):
        self._tasks.append(Thread(target=task, args=args))
        self._tasks[-1].start()

    def join(self):
        for task in self._tasks:
            task.join()


def handle_response(resp):
    match resp:
        case ErrorResponse(_, error_message):
            raise RuntimeError(f"Server error: {error_message}")
        case _:
            return resp


if __name__ == "__main__":
    num_of_players = 3
    game_name = f"yagde-test-game-{time.time()}"

    window = Window(1080, 1080, "YAGDE")
    game = Game()

    with ExitStack() as stack:
        observer_session = Session("wgforge-srv.wargaming.net", 443)
        stack.enter_context(observer_session)
        observer_info = handle_response(observer_session.login(
            LoginAction("yagde-test-user-observer",
                        game=game_name,
                        num_players=num_of_players,
                        is_observer=True)))

        players = []

        for i in range(num_of_players):
            session = Session("wgforge-srv.wargaming.net", 443)
            stack.enter_context(session)
            player_info = handle_response(session.login(
                LoginAction(f"yagde-test-user-{i}", game=game_name)))
            player_bot = Bot(session, player_info)
            players.append((player_bot, session))

        map_response = handle_response(observer_session.map())
        game.init_map(map_response)

        game_state = handle_response(observer_session.game_state())

        while not game_state.finished:
            game.update_state(game_state)

            window.draw(game)
            window.update()

            logging.info(f"Current player: {game_state.current_player_idx}")

            turns = TasksGroup()

            # Make current player turn
            for bot, session in players:
                if bot._playerInfo.idx != game_state.current_player_idx:
                    continue

                bot.update_vehicles(bot.collect_vehicles(game_state))
                map_response = handle_response(session.map())
                game_actions_response = handle_response(session.game_actions())

                bot.bot_engine(
                    game_state,
                    map_response,
                    game_actions_response
                )

                logging.info(f"Bot turn: {bot._playerInfo.idx}")

                turns.add(task=lambda s: handle_response(s.turn()),
                          args=(session,))

            # Make other players turns
            for bot, session in players:
                if bot._playerInfo.idx == game_state.current_player_idx:
                    continue

                logging.info(f"Bot turn: {bot._playerInfo.idx}")

                turns.add(task=lambda s: handle_response(s.turn()),
                          args=(session,))

            # Make observer turn
            logging.info(f"Observer turn: {observer_info.idx}")
            handle_response(observer_session.turn())

            turns.join()

            # Update game state
            game_state = handle_response(observer_session.game_state())

            # Wait for a while
            time.sleep(0.5)

        logging.info(f"Winner: {game_state.winner}")
