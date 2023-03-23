from typing import *

from client.common import *


class LoginAction(NamedTuple):
    name: str
    password: Optional[str] = None
    game: Optional[str] = None
    num_turns: Optional[int] = None
    num_players: Optional[int] = None
    is_observer: Optional[bool] = None


class ChatAction(NamedTuple):
    message: str


class MoveAction(NamedTuple):
    vehicle_id: VehicleId
    target: Hex


class ShootAction(NamedTuple):
    vehicle_id: VehicleId
    target: Hex
