from typing import *
from itertools import permutations

from client.common import Hex as ResponseHex


class Hex(NamedTuple):
    q: int
    r: int
    s: int

    def __add__(self, other):
        return Hex(self.q + other.q, self.r + other.r, self.s + other.s)

    def __sub__(self, other):
        return Hex(self.q - other.q, self.r - other.r, self.s - other.s)

    def distance(self, other=None):
        '''
        Returns the distance between two hexes.
        
        <param name="other">Other hex.</param>
        '''

        if other is None:
            other = Hex(0, 0, 0)

        return sum(map(abs, self - other)) // 2

    def neighbors(self, dist: int = 1):
        '''
        Returns the neighbors of the hex.
        
        <param name="dist">Distance from the hex to return neighbors at.</param>
        '''

        for diff in hexes_at(dist):
            yield self + diff

    def range(self, *args):
        '''
        Returns the hexes in the given range.
        
        <param name="args">Range to return hexes in.</param>
        '''

        for diff in hexes_range(*args):
            yield self + diff

    def on_line(self, other, obstacles):
        '''
        Returns if this hex is one one line with the other.
        
        <param name="other">Other hex.</param>
        '''

        if self.q == other.q or self.r == other.r or self.s == other.s:
            # Yes enemy is in range but let's check if there is obstacle between them
            if is_obstacle_betweenX(self, other, obstacles) or is_obstacle_betweenY(self, other, obstacles) or is_obstacle_betweenZ(self, other, obstacles):
                return False
            return True
        
        return False

    @staticmethod
    def from_hex_response(hex: ResponseHex):
        return Hex(*hex)


def hexes_at(dist: int = 0):
    '''
    Returns the hexes at the given distance from the origin.
    
    <param name="dist">Distance from the origin.</param>
    '''

    indexes = {0, 1, 2}
    result = set()
    for i, j in permutations(indexes, 2):
        k, = indexes - {i, j}
        sign = -1 if i > j else 1
        coords = [0] * 3
        coords[k] = sign * -dist
        for diff in range(dist + 1):
            coords[i] = sign * diff
            coords[j] = sign * (dist - diff)
            result.add(Hex(*coords))

    return result


def hexes_range(*args):
    '''
    Return hexes in the given range of distances from the origin.
    
    <param name="args">Range to return hexes in.</param>
    '''

    for dist in range(*args):
        for hex in hexes_at(dist):
            yield hex


def is_obstacle_betweenX(my_vehicle_position: Hex, enemy_vehicle_position: Hex, obstacles: List[Hex]) -> bool:
    '''Function that gives True if there is obstacle between my_vehicle_position and enemy_vehicle_position on x axis'''

    # There are 3 options for searching obstacles between
    if my_vehicle_position.q == enemy_vehicle_position.q:
        # Take lower coordinates for starting search
        j = my_vehicle_position.r+1 if my_vehicle_position.r < enemy_vehicle_position.r else enemy_vehicle_position.r+1
        k = my_vehicle_position.s+1 if my_vehicle_position.s < enemy_vehicle_position.s else enemy_vehicle_position.s+1

        # Take higher coordinates for end of a serach
        end_j = my_vehicle_position.r if my_vehicle_position.r > enemy_vehicle_position.r else enemy_vehicle_position.r

        while j < end_j: # Note here: we can check only one coordinate because the distance is same
            check_obstacle = Hex(my_vehicle_position.q, j, k)
            if check_obstacle in obstacles:
                return True
            j += 1
            k += 1
    return False

def is_obstacle_betweenY(my_vehicle_position: Hex, enemy_vehicle_position: Hex, obstacles: List[Hex]) -> bool:
    '''Function that gives True if there is obstacle between my_vehicle_position and enemy_vehicle_position on y axis'''

    # The rest are same, just different coordinates
    if my_vehicle_position.r == enemy_vehicle_position.r:
        # Take lower coordinates for starting search
        j = my_vehicle_position.q+1 if my_vehicle_position.q < enemy_vehicle_position.q else enemy_vehicle_position.q+1
        k = my_vehicle_position.s+1 if my_vehicle_position.s < enemy_vehicle_position.s else enemy_vehicle_position.s+1

        # Take higher coordinates for end of a serach
        end_j = my_vehicle_position.q if my_vehicle_position.q > enemy_vehicle_position.q else enemy_vehicle_position.q

        while j < end_j: # Note here: we can check only one coordinate because the distance is same
            check_obstacle = Hex(j, my_vehicle_position.r, k)
            if check_obstacle in obstacles:
                return True
            j += 1
            k += 1
    return False

def is_obstacle_betweenZ(my_vehicle_position: Hex, enemy_vehicle_position: Hex, obstacles: List[Hex]) -> bool:
    '''Function that gives True if there is obstacle between my_vehicle_position and enemy_vehicle_position on z axis'''

    if my_vehicle_position.s == enemy_vehicle_position.s:
        # Take lower coordinates for starting search
        j = my_vehicle_position.q+1 if my_vehicle_position.q < enemy_vehicle_position.q else enemy_vehicle_position.q+1
        k = my_vehicle_position.r+1 if my_vehicle_position.r < enemy_vehicle_position.r else enemy_vehicle_position.r+1

        # Take higher coordinates for end of a serach
        end_j = my_vehicle_position.q if my_vehicle_position.q > enemy_vehicle_position.q else enemy_vehicle_position.q

        while j < end_j: # Note here: we can check only one coordinate because the distance is same
            check_obstacle = Hex(j, k, my_vehicle_position.s)
            if check_obstacle in obstacles:
                return True
            j += 1
            k += 1
    return False