from typing import *
from enum import Enum

from client.common import *
from client.actions import ChatAction, MoveAction, ShootAction


class LoginResponse(NamedTuple):
    idx: PlayerId
    name: str
    is_observer: bool


class VehicleType(Enum):
    LIGHT_TANK = 0
    MEDIUM_TANK = 1
    HEAVY_TANK = 2
    AT_SPG = 3
    SPG = 4


class Vehicle(NamedTuple):
    player_id: PlayerId
    vehicle_type: VehicleType
    health: int
    spawn_position: Hex
    position: Hex
    capture_points: int
    shoot_range_bonus: int


class MapContent(Enum):
    BASE = 0
    OBSTAACLE = 1
    LIGHT_REPAIR = 2
    HARD_REPAIR = 3
    CATAPULT = 4


class MapResponse(NamedTuple):
    size: int
    name: str
    spawn_points: List[Mapping[VehicleType, List[Hex]]]
    content: Mapping[MapContent, List[Hex]]


class PlayerState(NamedTuple):
    idx: int
    name: str
    is_observer: bool


class WinPoints(NamedTuple):
    capture: int
    kill: int


class GameStateResponse(NamedTuple):
    num_players: int
    num_turns: int
    current_turn: int
    players: List[PlayerState]
    observers: List[str]  # don't know exact type
    current_player_idx: PlayerId
    finished: bool
    vehicles: Mapping[VehicleId, Vehicle]
    attack_matrix: Mapping[PlayerId, List[PlayerId]]  # don't know exact type
    winner: Optional[PlayerId]
    catapult_usage: List[Hex]


class PlayerAction(NamedTuple):
    player_id: PlayerId
    action_type: GameAction
    data: ChatAction | MoveAction | ShootAction  # depends on action_type


class GameActionsResponse(NamedTuple):
    actions: List[PlayerAction]


class ResponseCode(IntEnum):
    BAD_COMMAND = 1
    ACCESS_DENIED = 2
    INAPPROPRIATE_GAME_STATE = 3
    TIMEOUT = 4
    INTERNAL_SERVER_ERROR = 500


class ErrorResponse(NamedTuple):
    code: ResponseCode
    error_message: str
