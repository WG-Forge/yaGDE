from typing import *
from client.responses import *
from player.player import *
from ai.pathFinder import AStarPathfinding
from model.hex import Hex as MapHex


def check_range(game_actions: GameActionsResponse, my_vehicle: Vehicle, enemy_vehicle: Vehicle) -> bool:
    if my_vehicle.vehicle_type == VehicleType.MEDIUM_TANK:
        return Medium.is_enemy_in_range(game_actions, my_vehicle, enemy_vehicle)
    elif my_vehicle.vehicle_type == VehicleType.HEAVY_TANK:
        return Heavy.is_enemy_in_range(game_actions,my_vehicle, enemy_vehicle)
    elif my_vehicle.vehicle_type == VehicleType.LIGHT_TANK:
        return Light.is_enemy_in_range(game_actions,my_vehicle, enemy_vehicle)
    elif my_vehicle.vehicle_type == VehicleType.SPG:
        return SPG.is_enemy_in_range(game_actions,my_vehicle, enemy_vehicle)
    elif my_vehicle.vehicle_type == VehicleType.AT_SPG:
        return AT_SPG.is_enemy_in_range(game_actions,my_vehicle, enemy_vehicle)
    return False


class Medium:
    @staticmethod
    def is_enemy_in_range(game_actions: GameActionsResponse, my_vehicle: Vehicle, enemy_vehicle: Vehicle):
        distance = map_distance(my_vehicle.position, enemy_vehicle.position)
        if distance == 2:
             return True
        return False
    
    @staticmethod
    def move(path: list) -> Hex:
        moveHex = Hex(0, 0, 0)
        if len(path) >= 3:
            moveHex = Hex(*path[2])
        elif len(path) >= 2:
            moveHex = Hex(*path[1])
        return moveHex


class Heavy:
    @staticmethod
    def is_enemy_in_range(game_actions: GameActionsResponse, my_vehicle: Vehicle, enemy_vehicle: Vehicle):
        distance = map_distance(my_vehicle.position, enemy_vehicle.position)
        if distance <= 2:
            return True
        return False
    
    @staticmethod
    def move(path: list) -> Hex:
        moveHex = Hex(0, 0, 0)
        if len(path) >= 2:
            moveHex = Hex(*path[1])
        return moveHex


class Light:
    @staticmethod
    def is_enemy_in_range(game_actions: GameActionsResponse, my_vehicle: Vehicle, enemy_vehicle: Vehicle):
        distance = map_distance(my_vehicle.position, enemy_vehicle.position)
        if distance == 2:
            return True
        return False
    
    @staticmethod
    def move(path: list) -> Hex:
        moveHex = Hex(0, 0, 0)
        if len(path) >= 4:
            moveHex = Hex(*path[3])
        elif len(path) >= 3:
            moveHex = Hex(*path[2])
        elif len(path) >= 2:
            moveHex = Hex(*path[1])
        return moveHex
    

class SPG:
    @staticmethod
    def is_enemy_in_range(game_actions: GameActionsResponse, my_vehicle: Vehicle, enemy_vehicle: Vehicle):
        distance = map_distance(my_vehicle.position, enemy_vehicle.position)
        if distance == 3:
            return True
        return False
    
    @staticmethod
    def move(path: list) -> Hex:
        moveHex = Hex(0, 0, 0)
        if len(path) >= 2:
            moveHex = Hex(*path[1])
        return moveHex
    

class AT_SPG:
    @staticmethod
    def __two_out_of_three(my_position: Hex, enemy_position: Hex):
        return (my_position.x == enemy_position.x and my_position.y != enemy_position.y and my_position.z != enemy_position.z) or\
                (my_position.x != enemy_position.x and my_position.y == enemy_position.y and my_position.z != enemy_position.z) or\
                (my_position.x != enemy_position.x and my_position.y != enemy_position.y and my_position.z == enemy_position.z)

    @staticmethod
    def is_enemy_in_range(game_actions: GameActionsResponse, my_vehicle: Vehicle, enemy_vehicle: Vehicle):
        # TODO: maybe better algorithm can be used in future
        distance = map_distance(my_vehicle.position, enemy_vehicle.position)
        if distance <= 3 and AT_SPG.__two_out_of_three(my_vehicle.position, enemy_vehicle.position):
            return True
        return False
    
    @staticmethod
    def move(path: list) -> Hex:
        moveHex = Hex(0, 0, 0)
        if len(path) >= 2:
            moveHex = Hex(*path[1])
        return moveHex