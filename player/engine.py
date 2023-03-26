from typing import *
from client.responses import *
from client.session import Session
from player.player import *

maxHp = 2 # TODO: hardcode like this should be escaped in future

def handle_response(resp):
    match resp:
        case ErrorResponse(_, error_message):
            raise RuntimeError(f"Server error: {error_message}")
        case _:
            return resp


class Bot(Player):
    def __is_enemy_in_range(self, my_vehicle: Vehicle, enemy_vehicle: Vehicle) -> bool:
        distance = map_distance(my_vehicle['position'], enemy_vehicle['position'])
        if distance ==  2:
            return True
        return False
    
    def _shoot_with_vehicle(self, my_vehicle: Vehicle):
        target = None
        minHp = maxHp
        for vehicle_id, vehicle in self._enemyVehicle:
            if self.__is_enemy_in_range(self, my_vehicle, vehicle) and minHp >= vehicle['health']:
                minHp = vehicle['health']
                target = vehicle
        if target is not None:
            Player.shoot_vehicle(self, target)

    def bot_engine(self):
        while True:
            game_state = handle_response(self._session.game_state())
            if game_state.current_player_idx != self._playerInfo.idx:
                continue

            Player.update_vehicles(self, Player._collect_vehicles(self, game_state))

            if game_state.current_turn == game_state.num_turns:
                break
            game_map = handle_response(self._session.map())
            game_actions = handle_response(self._session.game_actions())
            # print(game_state.current_turn, game_map)
            handle_response(self._session.turn())