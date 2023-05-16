import logging
from contextlib import AsyncExitStack
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
from graphics.constants import WINDOW_NAME

from info import ( 
    SERVER_ADDR, 
    SERVER_PORT
)


game_name = "yagde-test-game"
num_of_players = 3
full = False
number_of_bots = 1

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s",
    level=logging.INFO)


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


async def create_sessions(stack: AsyncExitStack, game_name: str):
    observer_session = Session(SERVER_ADDR, SERVER_PORT)
    await stack.enter_async_context(observer_session)
    global full
    global num_of_players
    global number_of_bots
    observer_login = LoginAction("yagde-test-user-observer",
                                 game=game_name,
                                 num_players=num_of_players,
                                 is_observer=True,
                                 is_full=full)
    observer_info = handle_response(
        await observer_session.login(observer_login)
    )
    observer = Client(observer_info, observer_session)

    players = []
    for i in range(number_of_bots):
        player_session = Session(SERVER_ADDR, SERVER_PORT)
        await stack.enter_async_context(player_session)
        player_login = LoginAction(f"yagde-test-user-{i}", game=game_name, is_full=full)
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
    window_info = pygame.display.Info()
    window = Window(window_info.current_w, window_info.current_h, WINDOW_NAME)
    game = Game()
    global number_of_rounds
    async with AsyncExitStack() as stack:
        sessions = await create_sessions(stack, game_name)
        observer = sessions.observer
        

        map_response = handle_response(
            await observer.session.map()
        )

        game.init_map(map_response)

        while True:
            pygame.event.clear()
            game_state = handle_response(
                await observer.session.game_state()
            )
            game.update_state(game_state)

            if game_state.finished and game_state.current_round == game_state.num_rounds:
                break

            await make_turns(sessions, game_state.current_player_idx, game)

            # Get actions of this turn
            game_actions = handle_response(
                await observer.session.game_actions()
            )
            game.update_actions(game_actions)

            window.draw(game)
            window.update()
        

        logging.info(f"Winner: {game_state.winner}")

        w_name = ""
        for player in  game_state.players:
            if game_state.winner == player.idx:
                w_name = player.name

        window.end(w_name)


if __name__ == "__main__":
    sim_check = ""
    while sim_check.lower() != "y" and sim_check.lower() != "n":
        print("Do you want simulation?(Y/N) ", end="")
        sim_check = input()

    if sim_check.lower() == "n":
        number_of_bots = 1
        enter_type = ""
        while enter_type.lower() != 'j' and enter_type.lower() != 'c':
            print("Join or creating game? (J/C) ", end="")
            enter_type = input()

        if enter_type.lower() == "c":
            print("Enter number of players: ", end="")
            num_of_players = int(input())
            is_full = ""
            while is_full.lower() != "y" and is_full.lower() != "n":
                print("Is game full? (Y/N)", end="")
                is_full = input()

            if is_full.lower() == "y":
                full = True
            else:
                full = False
        else:
            num_of_players = 1

        print("Enter game name: ", end="")
        game_name = input()
    else:
        number_of_bots = 3
 
    pygame.init()
    aio.run(play())
