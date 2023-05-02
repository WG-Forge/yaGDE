from typing import *
from model.hex import *


class Node:
    def __init__(self, hex: Hex, end: Hex, g: int, prev: Hex):
        self.prev = prev
        self.g = g
        self.h = hex.distance(end)
        self.F = self.g + self.h

    def __repr__(self):
        return f"Node(prev={self.prev}, g={self.g}, h={self.h}, F={self.F})"

    def __lt__(self, other):
        return self.F < other.F


class AStarPathfinding:
    # Creates a new instance of AStarPathfinding.
    #
    # <param name="size">Size of the map.</param>
    # <param name="center">Center of the map.</param>
    def __init__(self, size: int = 10, center: Hex = Hex(0, 0, 0)):
        self.size = size
        self.center = center

    # Finds path from given start point to end point. Returns an empty list if the path couldn't be found.
    #
    # <param name="start">Start Hex.</param>
    # <param name="end">Destination Hex.</param>
    # <param name="exclude">Excluded nodes from search.</param>
    def path(self, start: Hex, end: Hex, exclude: Set[Hex] = {}) -> List[Hex]:
        # If the start or end Hex is excluded - return an empty list.
        if start in exclude or end in exclude:
            return []

        openNodes = {start: Node(start, end, 0, None)}
        closedNodes = dict()

        # While there are still nodes to check.
        while len(openNodes) != 0:

            # Popping the node with the lowest F value.
            currentHex = min(openNodes, key=openNodes.get)
            currentNode = openNodes[currentHex]
            del openNodes[currentHex]

            # Adding the current Hex to the closed list.
            closedNodes[currentHex] = currentNode

            # If the current Hex is the end Hex - we've found the path.
            if currentHex == end:
                break

            # Investigating each neighbor Hex of the current Hex.
            for neighborHex in currentHex.neighbors():

                # Ignoring too distant hexes.
                if neighborHex.distance(self.center) > self.size:
                    continue

                # Ignoring not walkable neighbors.
                if neighborHex in exclude:
                    continue

                # Ignoring the Hex if it's already closed.
                if neighborHex in closedNodes:
                    continue

                neighborNode = Node(neighborHex, end,
                                    currentNode.g + 1,
                                    currentHex)

                # If we discovered a new node or shorter path to an existing node - update the node.
                if neighborHex not in openNodes or neighborNode < openNodes[neighborHex]:
                    openNodes[neighborHex] = neighborNode

        finalPathHexes = []

        # Backtracking - setting the final path.
        current = end
        while current is not None and current in closedNodes:
            finalPathHexes.insert(0, current)
            current = closedNodes[current].prev

        return finalPathHexes
