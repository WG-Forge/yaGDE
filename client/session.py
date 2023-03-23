from typing import *

from client.actions import *
from client.responses import *


class Session:
    def __init__(self, addr: str):
        self.server_addr = addr

    def __enter__(self):
        self.connect()

    def __exit__(self, exc_type, exc_value, tb):
        self.disconnect()

    def connect(self):
        pass

    def disconnect(self):
        pass

    def login(self, action: LoginAction) -> LoginResponse | ErrorResponse:
        pass

    def logout(self) -> None | ErrorResponse:
        pass

    def map(self) -> MapResponse | ErrorResponse:
        pass

    def game_state(self) -> GameStateResponse | ErrorResponse:
        pass

    def game_actions(self) -> GameActionsResponse | ErrorResponse:
        pass

    def turn(self) -> None | ErrorResponse:
        pass

    def chat(self, action: ChatAction) -> None | ErrorResponse:
        pass

    def move(self, action: MoveAction) -> None | ErrorResponse:
        pass

    def shoot(self, action: ShootAction) -> None | ErrorResponse:
        pass
