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
    def __check_neutrality(self, game_actions: GameActionsResponse, target_vehicle: Vehicle):
        shot_actions = [action for action in game_actions.actions if action.action_type == GameAction.SHOOT]
        target_positions = [vehicle.position for vehicle in self._enemyVehicles.values() if target_vehicle.player_id == vehicle.player_id]
        ally_positions = [vehicle.position for vehicle in self._allyVehicles.values()]

        # check if target attacked me
        for action in shot_actions:
            if action.player_id == target_vehicle.player_id and action.data.target in ally_positions:
                return True

        # check if target was attacked in previous round
        for action in shot_actions:
            if action.player_id != target_vehicle.player_id and action.data.target in target_positions:
                return False
        # if he wasn't attacked just attack
        return True

    def __is_enemy_in_range(self, game_actions: GameActionsResponse, my_vehicle: Vehicle, enemy_vehicle: Vehicle) -> bool:
        distance = map_distance(my_vehicle.position, enemy_vehicle.position)
        if distance ==  2 and self.__check_neutrality(game_actions, enemy_vehicle):
            return True
        return False

    
    def _shoot_with_vehicle(self, my_vehicle_id: VehicleId, my_vehicle: Vehicle) -> bool:
        # this will be used for neutrality check
        game_actions = self._session.game_actions()

        target = None
        minHp = maxHp
        for vehicle_id, vehicle in self._enemyVehicles.items():
            if self.__is_enemy_in_range(game_actions, my_vehicle, vehicle) and minHp >= vehicle.health:
                minHp = vehicle.health
                target = vehicle
        if target is not None:
            Player.shoot_vehicle(self, my_vehicle_id, target)
            return True
        return False
    
    def __collectExcludedNodes(self) -> List:
        res = []
        # Nodes of all vehicles should be excluded from pathFinder algorithm
        for vehicle_id, vehicle in self._enemyVehicles.items():
            res.append(HexNode(vehicle.position.x, vehicle.position.y, vehicle.position.z))
        for vehicle_id, vehicle in self._allyVehicles.items():
            res.append(HexNode(vehicle.position.x, vehicle.position.y, vehicle.position.z))

        # All obstacles should be excluded as well
        map_response = self._session.map()
        if MapContent.OBSTACLE in map_response.content:
            for position in map_response.content[MapContent.OBSTACLE]:
                res.append(position)
        return res
    
    def __execute_movement(self, vehicle_id: VehicleId, vehicle: Vehicle) -> List:
        exclude = self.__collectExcludedNodes()

        # find next node to move
        path = AStarPathfinding.FindPath(HexNode(vehicle.position.x, vehicle.position.y, vehicle.position.z), HexNode(0, 0, 0), exclude)
        nextMovement = HexNode(0, 0, 0)
        if len(path) >= 2:
            nextMovement = path[1]
        elif len(path) >= 1:
            nextMovement = path[0]
        moveHex = Hex(nextMovement.x, nextMovement.y, nextMovement.z)
        self.move_vehicle(vehicle_id, moveHex)
        self._allyVehicles[vehicle_id] = self._allyVehicles[vehicle_id]._replace(position=Hex(nextMovement.x, nextMovement.y, nextMovement.z))

    def bot_engine(self):
        while True:
            game_state = handle_response(self._session.game_state())
            # TODO: should be done...
            if game_state.winner is not None:
                print("Someone won.")
                break

            if game_state.current_player_idx != self._playerInfo.idx:
                continue

            Player.update_vehicles(self, Player._collect_vehicles(self, game_state))

            if game_state.current_turn == game_state.num_turns:
                break
            
            # move each one of vehicles
            for vehicle_id, vehicle in self._allyVehicles.items():
                # try to shot
                shooted = self._shoot_with_vehicle(vehicle_id, vehicle)

                # now move to the center if didn't shot
                if shooted == False:
                    self.__execute_movement(vehicle_id, vehicle)

            handle_response(self._session.turn())