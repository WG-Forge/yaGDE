from enum import IntEnum
from typing import *


PlayerId = NewType("PlayerId", int)
PlayerId.from_json = lambda v: PlayerId(int(v))
VehicleId = NewType("VehicleId", int)
VehicleId.from_json = lambda v: VehicleId(int(v))


class Hex(NamedTuple):
    x: int
    y: int
    z: int

    def __eq__(self, other):
        return (self.x, self.y, self.z) == (other.x, other.y, other.z)

    @staticmethod
    def from_json(j) -> 'Hex':
        return Hex(**{
            k: int(j[k]) for k in Hex._fields
        })


class ProtocolAction(IntEnum):
    LOGIN = 1
    LOGOUT = 2
    MAP = 3
    GAME_STATE = 4
    GAME_ACTIONS = 5
    TURN = 6

    @staticmethod
    def from_json(j) -> 'ProtocolAction':
        return ProtocolAction(int(j))


class GameAction(IntEnum):
    CHAT = 100
    MOVE = 101
    SHOOT = 102

    @staticmethod
    def from_json(j) -> 'GameAction':
        return GameAction(int(j))


ActionType = ProtocolAction | GameAction


def enum_from_json(cls, j):
    for value in cls:
        if value.name.casefold() == j.casefold():
            return value

    raise ValueError(f"Unknown {cls} value: {j}")
