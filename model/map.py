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
        # Create GameMap from server MapResponse
        #
        # <param name="map_response">MapResponse from server</param>

        contents = {
            Hex.from_hex_response(hex): Content.from_content_response(content)
            for content, hexes in map_response.content.items()
            for hex in hexes
        }

        return GameMap(map_response.size, contents)

    def update_vehicles_from_state_response(self, state_response: GameStateResponse):
        # Update vehicles from server GameStateResponse
        #
        # <param name="state_response">GameStateResponse from server</param>

        self.vehicles = {
            Hex.from_hex_response(vehicle.position): Vehicle.from_vehicle_response(vid, vehicle)
            for vid, vehicle in state_response.vehicles.items()
        }

    def at(self, hex: Hex) -> Content | Vehicle | None:
        # Get content or vehicle at hex
        #
        # <param name="hex">Hex to get content or vehicle at</param>
        # <returns>Content or vehicle at hex or None if there is none</returns>

        if hex in self.vehicles:
            return self.vehicles[hex]
        if hex in self.content:
            return self.content[hex]
        return None

    def __repr__(self):
        return f"GameMap(size={self.size}, content={self.content}, vehicles={self.vehicles})"
