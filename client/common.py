from enum import IntEnum
from typing import *


PlayerId = NewType("PlayerId", int)
VehicleId = NewType("VehicleId", int)


class Hex(NamedTuple):
    x: int
    y: int
    z: int


class ProtocolAction(IntEnum):
    LOGIN = 1
    LOGOUT = 2
    MAP = 3
    GAME_STATE = 4
    GAME_ACTIONS = 5
    TURN = 6


class GameAction(IntEnum):
    CHAT = 100
    MOVE = 101
    SHOOT = 102


ActionType = ProtocolAction | GameAction
