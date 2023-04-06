from typing import *
from itertools import permutations


class Hex(NamedTuple):
    q: int
    r: int
    s: int

    def __add__(self, other):
        return Hex(self.q + other.q, self.r + other.r, self.s + other.s)

    def __sub__(self, other):
        return Hex(self.q - other.q, self.r - other.r, self.s - other.s)

    def distance(self, other=None):
        # Returns the distance between two hexes.
        #
        # <param name="other">Other hex.</param>

        if other is None:
            other = Hex(0, 0, 0)

        return sum(map(abs, self - other)) // 2

    def neighbors(self, dist: int = 1):
        # Returns the neighbors of the hex.
        #
        # <param name="dist">Distance from the hex to return neighbors at.</param>

        for diff in hexes_at(dist):
            yield self + diff

    def range(self, *args):
        # Returns the hexes in the given range.
        #
        # <param name="args">Range to return hexes in.</param>

        if len(args) == 1:
            end = args[0]
            start, step = 0, 1
        elif len(args) == 2:
            start, end = args
            step = 1
        else:
            start, end, step = args

        for dist in range(start, end, step):
            for neighbor in self.neighbors(dist):
                yield neighbor


def hexes_at(dist: int = 0):
    # Returns the hexes at the given distance from the origin.
    #
    # <param name="dist">Distance from the origin.</param>

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
