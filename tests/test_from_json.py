import unittest

from client.responses import *


class DeserializeTestCase(unittest.TestCase):
    def test_login_json(self):
        response = LoginResponse(
            idx=PlayerId(0),
            name="player",
            is_observer=False)
        data = {"idx": 0, "name": "player", "is_observer": False}
        result = LoginResponse.from_json(data)
        self.assertEqual(response, result)

    def test_map_json(self):
        response = MapResponse(
            size=11,
            name="test_map",
            spawn_points=[
                {
                    VehicleType.LIGHT_TANK: [Hex(0, 0, 0), Hex(1, 1, -2)],
                    VehicleType.MEDIUM_TANK: [Hex(1, 1, -2), Hex(0, 0, 0)],
                },
                {
                    VehicleType.HEAVY_TANK: [Hex(0, 0, 0), Hex(1, 1, -2)],
                    VehicleType.AT_SPG: [Hex(1, 1, -2), Hex(0, 0, 0)],
                }
            ],
            content={
                MapContent.BASE: [Hex(5, -5, 0), Hex(1, 2, -3)],
                MapContent.OBSTACLE: [Hex(1, 2, -3), Hex(5, -5, 0)],
            }
        )
        data = {
            "size": 11,
            "name": "test_map",
            "spawn_points": [
                {
                    "light_tank": [{"x": 0, "y": 0, "z": 0}, {"x": 1, "y": 1, "z": -2}],
                    "medium_tank": [{"x": 1, "y": 1, "z": -2}, {"x": 0, "y": 0, "z": 0}],
                },
                {
                    "heavy_tank": [{"x": 0, "y": 0, "z": 0}, {"x": 1, "y": 1, "z": -2}],
                    "at_spg": [{"x": 1, "y": 1, "z": -2}, {"x": 0, "y": 0, "z": 0}],
                }
            ],
            "content": {
                "base": [{"x": 5, "y": -5, "z": 0}, {"x": 1, "y": 2, "z": -3}],
                "obstacle": [{"x": 1, "y": 2, "z": -3}, {"x": 5, "y": -5, "z": 0}],
            }
        }
        result = MapResponse.from_json(data)
        self.assertEqual(response, result)

    def test_game_state_json(self):
        response = GameStateResponse(
            num_players=2,
            num_turns=100,
            current_turn=0,
            players=[
                PlayerState(
                    idx=PlayerId(0),
                    name="player0",
                    is_observer=False
                ),
                PlayerState(
                    idx=PlayerId(1),
                    name="player1",
                    is_observer=False
                )
            ],
            observers=[],
            current_player_idx=PlayerId(0),
            finished=False,
            vehicles={
                VehicleId(0): Vehicle(
                    player_id=PlayerId(0),
                    vehicle_type=VehicleType.LIGHT_TANK,
                    health=100,
                    spawn_position=Hex(-1, 1, 0),
                    position=Hex(-1, -1, 2),
                    capture_points=0,
                    shoot_range_bonus=0
                ),
                VehicleId(1): Vehicle(
                    player_id=PlayerId(1),
                    vehicle_type=VehicleType.MEDIUM_TANK,
                    health=100,
                    spawn_position=Hex(1, -1, 0),
                    position=Hex(1, 1, -2),
                    capture_points=0,
                    shoot_range_bonus=0
                )
            },
            attack_matrix={
                PlayerId(0): [PlayerId(1)],
                PlayerId(1): [PlayerId(0)]
            },
            win_points={
                PlayerId(0): WinPoints(
                    capture=10,
                    kill=10,
                ),
                PlayerId(1): WinPoints(
                    capture=0,
                    kill=0,
                )
            },
            winner=None,
            catapult_usage=[
                Hex(0, 0, 0), Hex(1, 1, -2)
            ]
        )
        data = {
            "num_players": 2,
            "num_turns": 100,
            "current_turn": 0,
            "players": [
                {
                    "idx": 0,
                    "name": "player0",
                    "is_observer": False
                },
                {
                    "idx": 1,
                    "name": "player1",
                    "is_observer": False
                }
            ],
            "observers": [],
            "current_player_idx": 0,
            "finished": False,
            "vehicles": {
                "0": {
                    "player_id": 0,
                    "vehicle_type": "light_tank",
                    "health": 100,
                    "spawn_position": {"x": -1, "y": 1, "z": 0},
                    "position": {"x": -1, "y": -1, "z": 2},
                    "capture_points": 0,
                    "shoot_range_bonus": 0
                },
                "1": {
                    "player_id": 1,
                    "vehicle_type": "medium_tank",
                    "health": 100,
                    "spawn_position": {"x": 1, "y": -1, "z": 0},
                    "position": {"x": 1, "y": 1, "z": -2},
                    "capture_points": 0,
                    "shoot_range_bonus": 0
                }
            },
            "attack_matrix": {
                "0": [1],
                "1": [0]
            },
            "win_points": {
                "0": {"capture": 10, "kill": 10},
                "1": {"capture": 0, "kill": 0}
            },
            "winner": None,
            "catapult_usage": [
                {"x": 0, "y": 0, "z": 0}, {"x": 1, "y": 1, "z": -2}
            ]
        }
        result = GameStateResponse.from_json(data)
        self.assertEqual(response, result)

    def test_game_actions_json(self):
        response = GameActionsResponse(
            actions=[
                PlayerAction(
                    player_id=PlayerId(0),
                    action_type=GameAction.MOVE,
                    data=MoveAction(
                        vehicle_id=VehicleId(0),
                        target=Hex(1, 1, -2),
                    )
                ),
                PlayerAction(
                    player_id=PlayerId(1),
                    action_type=GameAction.SHOOT,
                    data=ShootAction(
                        vehicle_id=VehicleId(1),
                        target=Hex(1, 1, -2),
                    )
                ),
                PlayerAction(
                    player_id=PlayerId(2),
                    action_type=GameAction.CHAT,
                    data=ChatAction(
                        message="Hello world!"
                    )
                )
            ]
        )
        data = {
            "actions": [
                {
                    "player_id": 0,
                    "action_type": GameAction.MOVE.value,
                    "data": {
                        "vehicle_id": 0,
                        "target": {"x": 1, "y": 1, "z": -2}
                    }
                },
                {
                    "player_id": 1,
                    "action_type": GameAction.SHOOT.value,
                    "data": {
                        "vehicle_id": 1,
                        "target": {"x": 1, "y": 1, "z": -2}
                    }
                },
                {
                    "player_id": 2,
                    "action_type": GameAction.CHAT.value,
                    "data": {
                        "message": "Hello world!"
                    }
                }
            ]
        }
        result = GameActionsResponse.from_json(data)
        self.assertEqual(response, result)
