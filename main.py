import logging
from contextlib import AsyncExitStack
import time
import asyncio as aio
import pygame

from client.session import Session
from client.actions import LoginAction, MoveAction as ClientMoveAction, ShootAction as ClientShootAction
from client.common import Hex as ClientHex, VehicleId as ClientVehicleId, PlayerId as ClientPlayerId
from client.responses import ErrorResponse
from player.engine import Engine
from model.game import Game
from model.common import PlayerId
from model.action import MoveAction, ShootAction
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


class Client:
    def __init__(self, info, session):
        self.info = info
        self.session = session


class Sessions:
    def __init__(self, observer, players):
        self.observer = observer
        self.players = players


async def send_action(session: Session, action):
    match action:
        case MoveAction(vehicleId=vehicleId, target=target):
            await session.move(ClientMoveAction(
                vehicle_id=ClientVehicleId(vehicleId),
                target=ClientHex(*target),
            ))
        case ShootAction(vehicleId=vehicleId, target=target):
            await session.shoot(ClientShootAction(
                vehicle_id=ClientVehicleId(vehicleId),
                target=ClientHex(*target),
            ))
        case _:
            raise RuntimeError(f"Unknown action type: {action}")


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
    observer = Client(observer_info, observer_session)

    players = []
    for i in range(num_of_players):
        player_session = Session(SERVER_ADDR, SERVER_PORT)
        await stack.enter_async_context(player_session)
        player_login = LoginAction(f"yagde-test-user-{i}", game=game_name)
        player_info = handle_response(
            await player_session.login(player_login)
        )
        players.append(Client(player_info, player_session))

    return Sessions(observer, players)


async def make_turns(sessions: Sessions, current_player_idx: ClientPlayerId, game: Game):
    observer = sessions.observer

    logging.info(f"Current player: {current_player_idx}")

    turn_tasks = []
    async with aio.TaskGroup() as turns:
        # Make current player turn
        for player in sessions.players:
            if player.info.idx != current_player_idx:
                continue

            engine = Engine(game, PlayerId(player.info.idx))

            logging.info(f"Bot turn: {player.info.idx}")

            actions = engine.make_turn()
            for action in actions:
                # TODO: Some actions fail (eg occupied hex in move), FIX IT
                await send_action(player.session, action)

            turn = turns.create_task(player.session.turn())
            turn_tasks.append(turn)

        # Make other players turns
        for player in sessions.players:
            if player.info.idx == current_player_idx:
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


async def play():
    num_of_players = 3
    game_name = f"yagde-test-game-{time.time()}"

    window = Window(1400, 980, "YAGDE")
    game = Game()

    async with AsyncExitStack() as stack:
        sessions = await create_sessions(stack, num_of_players, game_name)
        observer = sessions.observer

        map_response = handle_response(
            await observer.session.map()
        )

        game.init_map(map_response)

        while True:
            pygame.event.pump()
            game_state = handle_response(
                await observer.session.game_state()
            )
            game.update_state(game_state)

            if game_state.finished:
                await aio.sleep(1)
                break

            await make_turns(sessions, game_state.current_player_idx, game)

            # Get actions of this turn
            game_actions = handle_response(
                await observer.session.game_actions()
            )
            game.update_actions(game_actions)

            window.draw(game)
            window.update()

            # Wait for a while
            # await aio.sleep(1)

        logging.info(f"Winner: {game_state.winner}")

if __name__ == "__main__":
    pygame.init()
    aio.run(play())
