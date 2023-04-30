from typing import *

from ai.pathFinder import *
from model.hex import *
from model.game import *
from model.vehicle import *
from model.common import *
from model.action import *


VEHICLE_TURN_ORDER = [
    VehicleType.SPG,
    VehicleType.LIGHT_TANK,
    VehicleType.HEAVY_TANK,
    VehicleType.MEDIUM_TANK,
    VehicleType.AT_SPG
]


class Engine():

    def __init__(self, game: Game, player_id: PlayerId):
        self.game = game
        self.player_id = player_id
        self.actions = []
        self.path_finder = AStarPathfinding(game.map.size)

    def __shoot(self, vehicle: Vehicle, enemy: Vehicle):
        self.actions.append(
            ShootAction(self.player_id, vehicle.id, enemy.position)
        )

    def __move(self, vehicle: Vehicle, target: Hex):
        self.actions.append(
            MoveAction(self.player_id, vehicle.id, target)
        )

    def __shoot_with_vehicle(self, vehicle: Vehicle) -> bool:
        target = None

        for enemy in self.game.get_enemy_vehicles_for(self.player_id):
            can_attack = self.game.check_neutrality(vehicle, enemy)
            in_range = vehicle.in_shooting_range(enemy.position)

            if not can_attack or not in_range:
                continue

            if target is None or target.hp < enemy.hp:
                target = enemy

        if target is not None:
            self.__shoot(vehicle, target)
            return True

        return False

    def __move_vehicle(self, vehicle: Vehicle):
        obstacles = self.game.get_obstacles_for(self.player_id)
        target = Hex(0, 0, 0)

        path = self.path_finder.path(vehicle.position,
                                     target,
                                     obstacles)
        if path:
            move = vehicle.pick_move(path)
            self.__move(vehicle, move)

    def __vehicle_action(self, vehicle):
        shooted = self.__shoot_with_vehicle(vehicle)

        if shooted == False:
            self.__move_vehicle(vehicle)

    def make_turn(self):
        vehicles = self.game.get_vehicles_for(self.player_id)

        for vehicle_type in VEHICLE_TURN_ORDER:
            for vehicle in vehicles[vehicle_type]:
                self.__vehicle_action(vehicle)

        result = self.actions
        self.actions = []

        return result
