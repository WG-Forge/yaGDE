from enum import IntEnum
from typing import *


PlayerId = NewType("PlayerId", int)
VehicleId = NewType("VehicleId", int)


class Hex(NamedTuple):
    x: int
    y: int
    z: int


class ProtocolAction(IntEnum):
    LOGIN = 0
    LOGOUT = 1
    MAP = 2
    GAME_STATE = 3
    GAME_ACTIONS = 4
    TURN = 5


class GameAction(IntEnum):
    CHAT = 100
    MOVE = 101
    SHOOT = 102


Action = ProtocolAction | GameAction
