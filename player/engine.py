from typing import *

from client.responses import *
from client.session import Session
from player.player import *
from ai.pathFinder import AStarPathfinding
from model.hex import Hex as MapHex


from player.tanks import *


maxHp = 3


def handle_response(resp):
    match resp:
        case ErrorResponse(_, error_message):
            raise RuntimeError(f"Server error: {error_message}")
        case _:
            return resp


class Bot(Player):
    def __init__(self, s: Session, player_info: LoginResponse):
        super().__init__(s, player_info)
        self._pathFinder = AStarPathfinding()

    def __check_neutrality(self, game_actions: GameActionsResponse, target_vehicle: Vehicle):
        shot_actions = [
            action for action in game_actions.actions if action.action_type == GameAction.SHOOT]
        target_positions = [vehicle.position for vehicle in self._enemyVehicles.values(
        ) if target_vehicle.player_id == vehicle.player_id]
        ally_positions = [
            vehicle.position for vehicle in self._allyVehicles.values()]

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

    def _shoot_with_vehicle(self, my_vehicle_id: VehicleId, my_vehicle: Vehicle) -> bool:
        # this will be used for neutrality check
        game_actions = self._session.game_actions()

        target = None
        minHp = maxHp
        for vehicle_id, vehicle in self._enemyVehicles.items():
            if self.__check_neutrality(game_actions, vehicle) and check_range(game_actions, my_vehicle, vehicle) and minHp >= vehicle.health:
                minHp = vehicle.health
                target = vehicle
        if target is not None:
            Player.shoot_vehicle(self, my_vehicle_id, target)
            return True
        return False

    def __collectExcludedNodes(self, my_vehicle_id : VehicleId) -> List:
        res = []
        # Nodes of all vehicles should be excluded from pathFinder algorithm
        for vehicle_id, vehicle in self._enemyVehicles.items():
            res.append(MapHex(*vehicle.position))
        for vehicle_id, vehicle in self._allyVehicles.items():
            if vehicle_id == my_vehicle_id:
                continue
            res.append(MapHex(*vehicle.position))

        # All obstacles should be excluded as well
        map_response = self._session.map()
        if MapContent.OBSTACLE in map_response.content:
            for position in map_response.content[MapContent.OBSTACLE]:
                res.append(MapHex(*position))
        return res

    def __execute_movement(self, vehicle_id: VehicleId, vehicle: Vehicle) -> List:
        exclude = self.__collectExcludedNodes(vehicle_id)

        # find next node to move
        path = self._pathFinder.path(
            MapHex(*vehicle.position),
            MapHex(0, 0, 0),
            exclude)
        print("Path:")
        print(path)
        print('\n')
        moveHex = Hex(0, 0, 0)
        if vehicle.vehicle_type == VehicleType.SPG:
            moveHex = SPG.move(path)
        elif vehicle.vehicle_type == VehicleType.LIGHT_TANK:
            moveHex = Light.move(path)
        elif vehicle.vehicle_type == VehicleType.HEAVY_TANK:
            moveHex = Heavy.move(path)
        elif vehicle.vehicle_type == VehicleType.MEDIUM_TANK:
            moveHex = Medium.move(path)

        self.move_vehicle(vehicle_id, moveHex)
        self._allyVehicles[vehicle_id] = self._allyVehicles[vehicle_id]._replace(
            position=moveHex)

    def __vehicle_action(self, vehicles):
        # try to shot
        for vehicle_id, vehicle in vehicles.items():
            shooted = self._shoot_with_vehicle(vehicle_id, vehicle)

            # now move to the center if didn't shot
            if shooted == False:
                self.__execute_movement(vehicle_id, vehicle)


    def bot_engine(self):
        while True:
            game_state = handle_response(self._session.game_state())
            if game_state.winner is not None:
                print("Someone won.")
                break

            if game_state.current_player_idx != self._playerInfo.idx:
                continue

            Player.update_vehicles(
                self, Player._collect_vehicles(self, game_state))

            if game_state.current_turn == game_state.num_turns:
                break

            spg = {vehicle_id: vehicle for vehicle_id, vehicle in self._allyVehicles.items() if vehicle.vehicle_type == VehicleType.SPG}
            light = {vehicle_id: vehicle for vehicle_id, vehicle in self._allyVehicles.items() if vehicle.vehicle_type == VehicleType.LIGHT_TANK}
            heavy = {vehicle_id: vehicle for vehicle_id, vehicle in self._allyVehicles.items() if vehicle.vehicle_type == VehicleType.HEAVY_TANK}
            medium = {vehicle_id: vehicle for vehicle_id, vehicle in self._allyVehicles.items() if vehicle.vehicle_type == VehicleType.MEDIUM_TANK}
            at_spg = {vehicle_id: vehicle for vehicle_id, vehicle in self._allyVehicles.items() if vehicle.vehicle_type == VehicleType.AT_SPG}

            # move each one of vehicles
            self.__vehicle_action(spg)
            self.__vehicle_action(light)
            self.__vehicle_action(heavy)
            self.__vehicle_action(medium)
            self.__vehicle_action(at_spg)

            handle_response(self._session.turn())
