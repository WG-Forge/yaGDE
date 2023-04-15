from typing import *

from model.common import *
from model.vehicle import *
from client.responses import MapResponse, GameStateResponse


class GameMap:
    def __init__(self, size: int, content: Dict[Hex, Content]):
        self.size = size
        self.content = content
        self.vehicles = {}  # type: Dict[Hex, Vehicle]

    @staticmethod
    def from_map_response(map_response: MapResponse):
        content = {
            Hex.from_hex_response(hex): Content.from_content_response(content)
            for content, hexes in map_response.content.items()
            for hex in hexes
        }

        return GameMap(map_response.size, content)

    def update_vehicles_from_state_response(self, state_response: GameStateResponse):
        self.vehicles = {
            Hex.from_hex_response(vehicle.position): Vehicle.from_vehicle_response(vid, vehicle)
            for vid, vehicle in state_response.vehicles.items()
        }

    def __repr__(self):
        return f"GameMap(size={self.size}, content={self.content}, vehicles={self.vehicles})"
