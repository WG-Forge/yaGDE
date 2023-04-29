import logging
from contextlib import AsyncExitStack
import time
import asyncio as aio
import pygame

from client.session import Session
from client.actions import *
from client.responses import ErrorResponse
from player.player import Player
from player.engine import Bot
from model.hex import *
from model.game import Game
from model.map import GameMap
from model.action import TurnActions, MoveAction
from model.vehicle import *
from graphics.window import Window

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s",
    level=logging.INFO)

SERVER_ADDR = "wgforge-srv.wargaming.net"
SERVER_PORT = 443


def handle_response(resp):
    match resp:
        case ErrorResponse(_, error_message):
            raise RuntimeError(f"Server error: {error_message}")
        case _:
            return resp


class Player:
    def __init__(self, info, session):
        self.info = info
        self.session = session
        self.bot = Bot(self.session, self.info)


class Observer:
    def __init__(self, info, session):
        self.info = info
        self.session = session


class Sessions:
    def __init__(self, observer, players):
        self.observer = observer
        self.players = players


async def create_sessions(stack: AsyncExitStack, num_of_players: int, game_name: str):
    observer_session = Session(SERVER_ADDR, SERVER_PORT)
    await stack.enter_async_context(observer_session)
    observer_login = LoginAction("yagde-test-user-observer",
                                 game=game_name,
                                 num_players=num_of_players,
                                 is_observer=True)
    observer_info = handle_response(
        await observer_session.login(observer_login)
    )
    observer = Observer(observer_info, observer_session)

    players = []
    for i in range(num_of_players):
        player_session = Session(SERVER_ADDR, SERVER_PORT)
        await stack.enter_async_context(player_session)
        player_login = LoginAction(f"yagde-test-user-{i}", game=game_name)
        player_info = handle_response(
            await player_session.login(player_login)
        )
        players.append(Player(player_info, player_session))

    return Sessions(observer, players)


async def play():
    num_of_players = 3
    game_name = f"yagde-test-game-{time.time()}"

    window = Window(1400, 1200, "YAGDE")
    game = Game()

    async with AsyncExitStack() as stack:
        sessions = await create_sessions(stack, num_of_players, game_name)
        observer = sessions.observer

        map_response = handle_response(
            await observer.session.map()
        )
        game_state = handle_response(
            await observer.session.game_state()
        )

        game.init_map(map_response)

        while not game_state.finished:
            logging.info(f"Current player: {game_state.current_player_idx}")

            turn_tasks = []
            async with aio.TaskGroup() as turns:
                # Make current player turn
                for player in sessions.players:
                    if player.info.idx != game_state.current_player_idx:
                        continue

                    vehicles = player.bot.collect_vehicles(game_state)
                    player.bot.update_vehicles(vehicles)

                    map_response = handle_response(
                        await player.session.map()
                    )
                    game_actions_response = handle_response(
                        await player.session.game_actions()
                    )

                    await player.bot.bot_engine(
                        game_state,
                        map_response,
                        game_actions_response
                    )

                    logging.info(f"Bot turn: {player.info.idx}")

                    turn = turns.create_task(player.session.turn())
                    turn_tasks.append(turn)

                # Make other players turns
                for player in sessions.players:
                    if player.info.idx == game_state.current_player_idx:
                        continue

                    logging.info(f"Bot turn: {player.info.idx}")

                    turn = turns.create_task(player.session.turn())
                    turn_tasks.append(turn)

                # Make observer turn
                logging.info(f"Observer turn: {observer.info.idx}")
                turn = turns.create_task(observer.session.turn())
                turn_tasks.append(turn)

            for turn in turn_tasks:
                handle_response(turn.result())

            # Get actions of this turn
            actions = handle_response(
                await observer.session.game_actions()
            )

            game.update_state(game_state, actions)

            window.draw(game)
            window.update()

            # Request next game state
            game_state = handle_response(
                await observer.session.game_state()
            )

            # Wait for a while
            await aio.sleep(1)

        logging.info(f"Winner: {game_state.winner}")

if __name__ == "__main__":
    pygame.init()
    aio.run(play())
