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
            in_range = vehicle.in_shooting_range(enemy.position, self.game.map.get_obstacles_for(self.player_id))

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

        # We should get all other vehicles except this one
        other_vehicles = []
        for node, veh in self.game.map.vehicles.items():
            if veh.id == vehicle.id:
                continue
            other_vehicles.append(Hex(*veh.position))

        exclude = []
        for obst in obstacles:
            exclude.append(obst)
        for veh in other_vehicles:
            exclude.append(veh)

        # We should find closest base target that is reachable
        base_nodes = self.game.map.get_base_nodes(exclude)
        minDist = base_nodes[0].distance(vehicle.position)
        target = base_nodes[0]
        for node in base_nodes:
            dist = node.distance(vehicle.position)
            if dist < minDist:
                target = node
                minDist = dist

        path = self.path_finder.path(vehicle.position,
                                     target,
                                     exclude)

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
