from client.responses import MapResponse, GameStateResponse, GameActionsResponse
from model.vehicle import Vehicle, VehicleType
from model.map import GameMap
from model.common import PlayerId
from model.action import TurnActions
from ai.pathFinder import AStarPathfinding
from model.hex import Hex


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
    
    def is_obstacle_between(self, my_vehicle: Vehicle, destination: Hex):
        path = AStarPathfinding().path(my_vehicle.position,
                                       destination,
                                       self.map.get_obstacles_for(my_vehicle.playerId),
                                       1)
        if len(path) <= my_vehicle.speed + 1:
            return False
        return True
    
    def on_line(self, vehicle: Vehicle, target: Hex):
        '''
        Returns if this hex is one one line with the other and if there is no obstacle between them.
        
        <param name="other">Other hex.</param>
        '''

        if vehicle.position.q == target.q or vehicle.position.r == target.r or vehicle.position.s == target.s:
            # Other is aligned to the hex, let's check if there is obstacle between them
            if not self.is_obstacle_between(vehicle, target):
                return True
        return False
    
    def in_shooting_range(self, vehicle: Vehicle, target: Hex) -> bool:
        dist = vehicle.position.distance(target)
        rl, ru = vehicle.shooting_range
        if vehicle.bonus:
            ru += 1
        in_range = rl <= dist <= ru

        match vehicle.type:
            case VehicleType.AT_SPG:
                return in_range and self.on_line(vehicle, target)
            case _:
                return in_range

    def get_vehicles_for(self, player: PlayerId):
        return self.map.get_vehicles_for(player)

    def get_enemy_vehicles_for(self, player: PlayerId):
        return self.map.get_enemy_vehicles_for(player)

    def get_obstacles_for(self, player: PlayerId):
        return self.map.get_obstacles_for(player)
