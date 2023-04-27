from client.responses import *
from model.map import GameMap
from model.common import PlayerId


class Game:
    def __init__(self):
        self.map = None
        self.players = None

    def init_map(self, map_response: MapResponse):
        # Initialize map from server MapResponse
        #
        # <param name="map_response">MapResponse from server</param>

        self.map = GameMap.from_map_response(map_response)

    def update_state(self, state_response: GameStateResponse):
        # Update map and players from server GameStateResponse
        #
        # <param name="state_response">GameStateResponse from server</param>

        self.map.update_vehicles_from_state_response(state_response)
        self.players = [PlayerId(player.idx)
                        for player in state_response.players]
