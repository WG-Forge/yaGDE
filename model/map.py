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

    def get_spawn_points(self) -> List[Hex]:
        # Get spawn points
        #
        # <returns>List of spawn points</returns>

        return [vehicle.spawn for vehicle in self.vehicles.values()]

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

    def vehicle_by(self, id: VehicleId) -> Vehicle | None:
        # Get vehicle by id
        #
        # <param name="id">Vehicle id</param>
        # <returns>Vehicle with id or None if there is none</returns>

        # TODO: This is O(n) and should be O(1)
        for vehicle in self.vehicles.values():
            if vehicle.id == id:
                return vehicle

        return None

    def get_vehicles_for(self, player_id: PlayerId) -> Dict[VehicleType, List[Vehicle]]:
        # Get vehicles for player
        #
        # <param name="player_id">Player id</param>
        # <returns>Dictionary of vehicle type to list of vehicles</returns>

        vehicles = {}  # type: Dict[VehicleType, List[Vehicle]]
        for vehicle in self.vehicles.values():
            if vehicle.playerId != player_id:
                continue

            if vehicle.type not in vehicles:
                vehicles[vehicle.type] = []

            vehicles[vehicle.type].append(vehicle)

        return vehicles

    def get_enemy_vehicles_for(self, player_id: PlayerId) -> List[Vehicle]:
        # Get enemy vehicles for player
        #
        # <param name="player_id">Player id</param>
        # <returns>List of enemy vehicles</returns>

        return [
            vehicle
            for vehicle in self.vehicles.values()
            if vehicle.playerId != player_id
        ]

    def get_obstacles_for(self, player_id: PlayerId) -> List[Hex]:
        # Get obstacles for player, i.e. hexes vahicles cannot move through
        #
        # <param name="player_id">Player id</param>
        # <returns>List of obstacles</returns>

        # Are enemy vehicles obstacles?
        return [hex for hex, content in self.contents.items()
                if content == Content.OBSTACLE]

    def __repr__(self):
        return f"GameMap(size={self.size}, content={self.content}, vehicles={self.vehicles})"
