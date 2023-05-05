from typing import *

from model.hex import Hex
from model.common import *
from client.responses import Vehicle as ResponseVehicle
from client.common import VehicleId as ResponseVehicleId
from client.responses import VehicleType as ResponseVehicleType

VehicleId = NewType('VehicleId', int)


class VehicleType(Enum):
    LIGHT_TANK = 0
    MEDIUM_TANK = 1
    HEAVY_TANK = 2
    AT_SPG = 3
    SPG = 4

    @staticmethod
    def from_reponse_vehicle_type(response: ResponseVehicleType) -> 'VehicleType':
        match response:
            case ResponseVehicleType.LIGHT_TANK:
                return VehicleType.LIGHT_TANK
            case ResponseVehicleType.MEDIUM_TANK:
                return VehicleType.MEDIUM_TANK
            case ResponseVehicleType.HEAVY_TANK:
                return VehicleType.HEAVY_TANK
            case ResponseVehicleType.AT_SPG:
                return VehicleType.AT_SPG
            case ResponseVehicleType.SPG:
                return VehicleType.SPG
            case _:
                raise ValueError(f"Unknown vehicle type response: {response}")


VEHICLE_MAX_HP = {
    VehicleType.LIGHT_TANK: 1,
    VehicleType.MEDIUM_TANK: 2,
    VehicleType.HEAVY_TANK: 3,
    VehicleType.AT_SPG: 2,
    VehicleType.SPG: 1,
}

VEHICLE_SPEED_POINTS = {
    VehicleType.LIGHT_TANK: 3,
    VehicleType.MEDIUM_TANK: 2,
    VehicleType.HEAVY_TANK: 1,
    VehicleType.AT_SPG: 1,
    VehicleType.SPG: 1,
}

VEHICLE_DAMAGE_POINTS = {
    VehicleType.LIGHT_TANK: 1,
    VehicleType.MEDIUM_TANK: 1,
    VehicleType.HEAVY_TANK: 1,
    VehicleType.AT_SPG: 1,
    VehicleType.SPG: 1,
}

VEHICLE_SHOOTING_RANGE = {
    VehicleType.LIGHT_TANK: (2, 2),
    VehicleType.MEDIUM_TANK: (2, 2),
    VehicleType.HEAVY_TANK: (1, 2),
    VehicleType.AT_SPG: (1, 3),
    VehicleType.SPG: (3, 3),
}


class Vehicle:
    def __init__(self, id: VehicleId, playerId: PlayerId,
                 vehicle_type: VehicleType, spawn: Hex,
                 hp: int, position: Hex, bonus: bool):
        self.id = id
        self.playerId = playerId
        self.type = vehicle_type
        self.hp = hp
        self.max_hp = VEHICLE_MAX_HP[vehicle_type]
        self.speed = VEHICLE_SPEED_POINTS[vehicle_type]
        self.damage = VEHICLE_DAMAGE_POINTS[vehicle_type]
        self.shooting_range = VEHICLE_SHOOTING_RANGE[vehicle_type]
        self.position = position
        self.spawn = spawn
        self.bonus = bonus

    @staticmethod
    def from_vehicle_response(vid: ResponseVehicleId, vehicle: ResponseVehicle):
        return Vehicle(
            id=VehicleId(vid),
            playerId=PlayerId(vehicle.player_id),
            vehicle_type=VehicleType.from_reponse_vehicle_type(vehicle.vehicle_type),
            spawn=Hex.from_hex_response(vehicle.spawn_position),
            hp=vehicle.health,
            position=Hex.from_hex_response(vehicle.position),
            bonus=vehicle.shoot_range_bonus==1
        )

    def in_shooting_range(self, target: Hex, obstacles: List[Hex]) -> bool:
        dist = self.position.distance(target)
        rl, ru = self.shooting_range
        if self.bonus:
            ru += 1
        in_range = rl <= dist <= ru

        match self.type:
            case VehicleType.AT_SPG:
                return in_range and self.position.on_line(target, obstacles)
            case _:
                return in_range

    def pick_move(self, path):
        '''
        Pick move target from path
        
        <param name="path">Path to target</param>
        <returns>Move target</returns>
        '''

        if len(path) > self.speed:
            return path[self.speed]
        else:
            return path[-1]

    def __repr__(self):
        return f"Vehicle(id={self.id}, playerId={self.playerId}, type={self.type}, hp={self.hp}, position={self.position})"
