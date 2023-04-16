from typing import *

from model.common import *
from model.vehicle import *
from client.responses import MapResponse, GameStateResponse


class GameMap:
    def __init__(self, size: int, contents: Dict[Hex, Content]):
        self.size = size
        self.contents = contents
        self.vehicles = {}  # type: Dict[Hex, Vehicle]

    @staticmethod
    def from_map_response(map_response: MapResponse):
        contents = {
            Hex.from_hex_response(hex): Content.from_content_response(content)
            for content, hexes in map_response.content.items()
            for hex in hexes
        }

        return GameMap(map_response.size, contents)

    def update_vehicles_from_state_response(self, state_response: GameStateResponse):
        self.vehicles = {
            Hex.from_hex_response(vehicle.position): Vehicle.from_vehicle_response(vid, vehicle)
            for vid, vehicle in state_response.vehicles.items()
        }

    def at(self, hex: Hex) -> Content | Vehicle | None:
        if hex in self.vehicles:
            return self.vehicles[hex]
        if hex in self.content:
            return self.content[hex]
        return None

    def __repr__(self):
        return f"GameMap(size={self.size}, content={self.content}, vehicles={self.vehicles})"
