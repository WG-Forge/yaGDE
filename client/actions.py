from typing import Optional, NamedTuple


from client.common import Hex, VehicleId


class LoginAction(NamedTuple):
    name: str
    password: Optional[str] = None
    game: Optional[str] = None
    num_turns: Optional[int] = None
    num_players: Optional[int] = None
    is_observer: Optional[bool] = None


class ChatAction(NamedTuple):
    message: str

    @staticmethod
    def from_json(j) -> 'ChatAction':
        return ChatAction(message=str(j["message"]))


class MoveAction(NamedTuple):
    vehicle_id: VehicleId
    target: Hex

    @staticmethod
    def from_json(j) -> 'MoveAction':
        return MoveAction(
            vehicle_id=VehicleId.from_json(j['vehicle_id']),
            target=Hex.from_json(j['target']),
        )


class ShootAction(NamedTuple):
    vehicle_id: VehicleId
    target: Hex

    @staticmethod
    def from_json(j) -> 'ShootAction':
        return ShootAction(
            vehicle_id=VehicleId.from_json(j['vehicle_id']),
            target=Hex.from_json(j['target']),
        )


Action = LoginAction | ChatAction | MoveAction | ShootAction
