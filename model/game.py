from client.responses import MapResponse, GameStateResponse, GameActionsResponse
from model.vehicle import Vehicle
from model.map import GameMap
from model.common import PlayerId
from model.action import TurnActions


class Game:
    def __init__(self):
        self.map = None
        self.players = None
        self.turns = None

    def init_map(self, map_response: MapResponse):
        '''
        Initialize map from server MapResponse
        
        <param name="map_response">MapResponse from server</param>
        '''

        self.map = GameMap.from_map_response(map_response)

    def update_state(self, state_response: GameStateResponse):
        '''
        Update map and players from server GameStateResponse
        
        <param name="state_response">GameStateResponse from server</param>
        '''

        self.map.update_vehicles_from_state_response(state_response)
        self.players = [PlayerId(player.idx)
                        for player in state_response.players]
        self.attack_matrix = {PlayerId(idx): [PlayerId(idx) for idx in matrix]
                              for idx, matrix in state_response.attack_matrix.items()}

    def update_actions(self, actions: GameActionsResponse):
        '''
        Update actions from server GameActionsResponse

        <param name="actions">GameActionsResponse from server</param>
        '''

        self.actions = TurnActions.from_actions_response(actions)

    def check_neutrality(self, vehicle: Vehicle, enemy: Vehicle):
        '''
        Check if vehicle can attack enemy
        
        <param name="vehicle">Vehicle to check</param>
        <param name="enemy">Enemy to check</param>
        <returns>True if vehicle can attack enemy, False otherwise</returns>
        '''

        player_id = vehicle.playerId
        enemy_id = enemy.playerId

        was_attacked = any(
            enemy_id in attacked for attacked in self.attack_matrix.values()
        )
        attacked_player = player_id in self.attack_matrix[enemy_id]

        return not was_attacked or attacked_player

    def get_vehicles_for(self, player: PlayerId):
        return self.map.get_vehicles_for(player)

    def get_enemy_vehicles_for(self, player: PlayerId):
        return self.map.get_enemy_vehicles_for(player)

    def get_obstacles_for(self, player: PlayerId):
        return self.map.get_obstacles_for(player)
