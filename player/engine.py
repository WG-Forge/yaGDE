from typing import *
from client.responses import *
from client.session import Session
from player.player import *
from AI_Logic.pathFinder import AStarPathfinding
from AI_Logic.pathFinder import HexNode

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
    
    def _shoot_with_vehicle(self, my_vehicle_id: VehicleId, my_vehicle: Vehicle) -> bool:
        target = None
        minHp = maxHp
        for vehicle_id, vehicle in self._enemyVehicle.items():
            if self.__is_enemy_in_range(self, my_vehicle, vehicle) and minHp >= vehicle.health:
                minHp = vehicle.health
                target = vehicle
        if target is not None:
            Player.shoot_vehicle(self, my_vehicle_id, target)
            return True
        return False
    
    def __collectExcludedNodes(self) -> List:
        res = []
        for vehicle_id, vehicle in self._enemyVehicle.items():
            res.append(HexNode(vehicle.position.x, vehicle.position.y, vehicle.position.z))
        for vehicle_id, vehicle in self._allyVehicles.items():
            res.append(HexNode(vehicle.position.x, vehicle.position.y, vehicle.position.z))
        return res
    
    def __execute_movement(self, vehicle_id: VehicleId, vehicle: Vehicle) -> List:
        exclude = self.__collectExcludedNodes()
        path = AStarPathfinding.FindPath(HexNode(vehicle.position.x, vehicle.position.y, vehicle.position.z), HexNode(0, 0, 0), exclude)
        nextMovement = HexNode(0, 0, 0)
        if len(path) >= 2:
            nextMovement = path[1]
        elif len(path) >= 1:
            nextMovement = path[0]
        # self._session.move(MoveAction(vehicle_id, Hex(nextMovement.x, nextMovement.y, nextMovement.z)))
        moveHex = Hex(nextMovement.x, nextMovement.y, nextMovement.z)
        self.move_vehicle(vehicle_id, moveHex)
        self._allyVehicles[vehicle_id] = self._allyVehicles[vehicle_id]._replace(position=Hex(nextMovement.x, nextMovement.y, nextMovement.z))

    def bot_engine(self):
        while True:
            game_state = handle_response(self._session.game_state())
            if game_state.current_player_idx != self._playerInfo.idx:
                continue

            Player.update_vehicles(self, Player._collect_vehicles(self, game_state))

            if game_state.current_turn == game_state.num_turns:
                break

            game_map = handle_response(self._session.map())
            
            # move each one of vehicles
            for vehicle_id, vehicle in self._allyVehicles.items():
                # try to shot
                shooted = self._shoot_with_vehicle(vehicle_id, vehicle)

                # now move to the center
                self.__execute_movement(vehicle_id, vehicle)

                # if didn't use shot use it now
                if shooted == False:
                    self._shoot_with_vehicle(vehicle_id, vehicle)

            game_actions = handle_response(self._session.game_actions())
            handle_response(self._session.turn())