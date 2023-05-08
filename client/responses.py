from typing import List, Dict, Optional, NamedTuple
from enum import Enum

from client.common import (
    PlayerId, 
    Hex, 
    enum_from_json, 
    VehicleId, 
    GameAction, 
    IntEnum, 
    ActionType, 
    ProtocolAction
)

from client.actions import ChatAction, MoveAction, ShootAction


class LoginResponse(NamedTuple):
    idx: PlayerId
    name: str
    is_observer: bool

    @staticmethod
    def from_json(j) -> 'LoginResponse':
        return LoginResponse(
            idx=PlayerId.from_json(j['idx']),
            name=str(j['name']),
            is_observer=bool(j['is_observer']),
        )


class VehicleType(Enum):
    LIGHT_TANK = 0
    MEDIUM_TANK = 1
    HEAVY_TANK = 2
    AT_SPG = 3
    SPG = 4

    @staticmethod
    def from_json(j) -> 'VehicleType':
        return enum_from_json(VehicleType, j)


class Vehicle(NamedTuple):
    player_id: PlayerId
    vehicle_type: VehicleType
    health: int
    spawn_position: Hex
    position: Hex
    capture_points: int
    shoot_range_bonus: int

    @staticmethod
    def from_json(j) -> 'Vehicle':
        return Vehicle(
            player_id=PlayerId.from_json(j['player_id']),
            vehicle_type=VehicleType.from_json(j['vehicle_type']),
            health=int(j['health']),
            spawn_position=Hex.from_json(j['spawn_position']),
            position=Hex.from_json(j['position']),
            capture_points=int(j['capture_points']),
            shoot_range_bonus=int(j['shoot_range_bonus']
                                  ) if 'shoot_range_bonus' in j else -1,
        )


class MapContent(Enum):
    BASE = 0
    OBSTACLE = 1
    LIGHT_REPAIR = 2
    HARD_REPAIR = 3
    CATAPULT = 4

    @staticmethod
    def from_json(j) -> 'MapContent':
        return enum_from_json(MapContent, j)


class MapResponse(NamedTuple):
    size: int
    name: str
    spawn_points: List[Dict[VehicleType, List[Hex]]]
    content: Dict[MapContent, List[Hex]]

    @staticmethod
    def from_json(j) -> 'MapResponse':
        return MapResponse(
            size=int(j['size']),
            name=str(j['name']),
            spawn_points=[
                {
                    VehicleType.from_json(k): [Hex.from_json(h) for h in v]
                    for k, v in spawn_point.items()
                }
                for spawn_point in j['spawn_points']
            ],
            content={
                MapContent.from_json(k): [Hex.from_json(h) for h in v]
                for k, v in j['content'].items()
            },
        )


class PlayerState(NamedTuple):
    idx: PlayerId
    name: str
    is_observer: bool

    @staticmethod
    def from_json(j) -> 'PlayerState':
        return PlayerState(
            idx=PlayerId.from_json(j['idx']),
            name=str(j['name']),
            is_observer=bool(j['is_observer']),
        )


class WinPoints(NamedTuple):
    player_id = PlayerId
    capture: int
    kill: int

    @staticmethod
    def from_json(j) -> 'WinPoints':
        return WinPoints(
            capture=int(j['capture']),
            kill=int(j['kill']),
        )


class GameStateResponse(NamedTuple):
    num_players: int
    num_turns: int
    current_turn: int
    players: List[PlayerState]
    observers: List[PlayerState]
    current_player_idx: Optional[PlayerId]
    finished: bool
    vehicles: Dict[VehicleId, Vehicle]
    attack_matrix: Dict[PlayerId, List[PlayerId]]  # don't know exact type
    win_points: Dict[PlayerId, WinPoints]
    winner: Optional[PlayerId]
    catapult_usage: List[Hex]

    @staticmethod
    def from_json(j) -> 'GameStateResponse':
        return GameStateResponse(
            num_players=int(j['num_players']),
            num_turns=int(j['num_turns']),
            current_turn=int(j['current_turn']),
            players=[PlayerState.from_json(p) for p in j['players']],
            observers=[PlayerState.from_json(o) for o in j['observers']],
            current_player_idx=PlayerId.from_json(j['current_player_idx'])
            if 'current_player_idx' in j and j['current_player_idx']
            else None,
            finished=bool(j['finished']),
            vehicles={
                VehicleId.from_json(k): Vehicle.from_json(v)
                for k, v in j['vehicles'].items()
            },
            attack_matrix={
                PlayerId.from_json(k): [PlayerId.from_json(p) for p in v]
                for k, v in j['attack_matrix'].items()
            },
            win_points={PlayerId.from_json(k): WinPoints.from_json(v)
                        for k, v in j['win_points'].items()},
            winner=PlayerId.from_json(j['winner'])
            if 'winner' in j and j['winner']
            else None,
            catapult_usage=[Hex.from_json(
                h) for h in j['catapult_usage']] if 'catapult_usage' in j else [],
        )


class PlayerAction(NamedTuple):
    player_id: PlayerId
    action_type: GameAction
    data: ChatAction | MoveAction | ShootAction  # depends on action_type

    @staticmethod
    def from_json(j) -> 'PlayerAction':
        action_type = GameAction.from_json(j['action_type'])
        match action_type:
            case GameAction.CHAT:
                data = ChatAction.from_json(j['data'])
            case GameAction.MOVE:
                data = MoveAction.from_json(j['data'])
            case GameAction.SHOOT:
                data = ShootAction.from_json(j['data'])

        return PlayerAction(
            player_id=PlayerId.from_json(j['player_id']),
            action_type=action_type,
            data=data
        )


class GameActionsResponse(NamedTuple):
    actions: List[PlayerAction]

    @staticmethod
    def from_json(j) -> 'GameActionsResponse':
        return GameActionsResponse(
            actions=[PlayerAction.from_json(a) for a in j['actions']]
        )


ActionResponse = LoginResponse | MapResponse | GameStateResponse | GameActionsResponse


class ResponseCode(IntEnum):
    OKEY = 0
    BAD_COMMAND = 1
    ACCESS_DENIED = 2
    INAPPROPRIATE_GAME_STATE = 3
    TIMEOUT = 4
    INTERNAL_SERVER_ERROR = 500


class ErrorResponse(NamedTuple):
    code: ResponseCode
    error_message: str
