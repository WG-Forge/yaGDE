from typing import *

from client.responses import *
from client.actions import *
from client.session import Session


Vehicles = NewType("Vehicles", Mapping[VehicleId, Vehicle])


def map_distance(node1: Hex, node2: Hex):
    return (abs(node1['x'] - node2['x']) + abs(node1['y'] - node2['y']) + abs(node1['z'] - node2['z'])) / 2


class Player:
    def __init__(self, s: Session, info: LoginResponse):
        self._playerInfo = info
        self._session = s
        self._allyVehicles = {}
        self._enemyVehicles = {}

    def _collect_vehicles(self, response: GameStateResponse) -> Vehicles:
        return response.vehicles

    def update_vehicles(self, vehicles: Vehicles):
        self._allyVehicles = {vehicle_id: vehicle for vehicle_id, vehicle in vehicles.items(
        ) if vehicle['player_id'] == self._playerInfo.idx}
        self._enemyVehicle = {vehicle_id: vehicle for vehicle_id, vehicle in vehicles.items(
        ) if vehicle['player_id'] != self._playerInfo.idx}

    def move_vehicle(self, vehicle_id: VehicleId, x: int, y: int, z: int):
        self._session.move(MoveAction(vehicle_id, Hex(x, y, z)))

    def shoot_vehicle(self, vehicle_id: VehicleId, x: int, y: int, z: int):
        self._session.shoot(ShootAction(vehicle_id, Hex(x, y, z)))
