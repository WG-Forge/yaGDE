from model.common import *
from model.vehicle import *
from model.hex import Hex
from client.responses import GameActionsResponse, GameAction


class ChatAction:
    def __init__(self, playerId: PlayerId, message: str):
        self.playerId = playerId
        self.message = message


class MoveAction:
    def __init__(self, playerId: PlayerId, vehicleId: VehicleId, target: Hex):
        self.playerId = playerId
        self.vehicleId = vehicleId
        self.target = target


class ShootAction:
    def __init__(self, playerId: PlayerId, vehicleId: VehicleId, target: Hex):
        self.playerId = playerId
        self.vehicleId = vehicleId
        self.target = target


class TurnActions:
    def __init__(self, moves, shoots, chats):
        self.moves = moves
        self.shoots = shoots
        self.chats = chats

    @staticmethod
    def from_actions_response(reponse: GameActionsResponse):
        moves = []
        shoots = []
        chats = []

        for action in reponse.actions:
            match action.action_type:
                case GameAction.MOVE:
                    moves.append(MoveAction(
                        playerId=PlayerId(action.player_id),
                        vehicleId=VehicleId(action.data.vehicle_id),
                        target=Hex.from_hex_response(action.data.target),
                    ))
                case GameAction.SHOOT:
                    shoots.append(ShootAction(
                        playerId=PlayerId(action.player_id),
                        vehicleId=VehicleId(action.data.vehicle_id),
                        target=Hex.from_hex_response(action.data.target),
                    ))
                case GameAction.CHAT:
                    chats.append(ChatAction(
                        playerId=PlayerId(action.player_id),
                        message=action.data.message,
                    ))

        return TurnActions(
            moves=moves,
            shoots=shoots,
            chats=chats,
        )
