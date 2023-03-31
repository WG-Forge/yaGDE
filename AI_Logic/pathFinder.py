
class HexNode:
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z
        #A* attributes
        self.g = 0
        self.h = 0
        self.F = 0


    def __eq__(self, other):
        return (self.x, self.y, self.z) == (other.x, other.y, other.z)

    def __repr__(self):
        return str(self.x) + " " + str(self.y) + " " + str(self.z)


class AStarPathfinding:

    # Finds path from given start point to end point. Returns an empty list if the path couldn't be found.
    # 
    # <param name="startPoint">Start Hex.</param>
    # <param name="endPoint">Destination Hex.</param>
    # <param name="list_exclude_nodes">Excluded nodes from search.</param>
    # Trenutno ne proverava granice HEX mape jer idemo samo ka centru ali ako se to promeni onda se mora dodati i ta provera
    @staticmethod
    def FindPath(start_point: HexNode, end_point: HexNode, list_exclude_nodes: []) -> list:
        openPathHexs = []
        closedPathHexs = []

        # Prepare the start Hex.
        currentHex = start_point

        currentHex.g = 0
        currentHex.h = AStarPathfinding.GetEstimatedPathCost(start_point, end_point)
        currentHex.F = currentHex.g + currentHex.h

        # append the start Hex to the open list.
        openPathHexs.append(currentHex)

        while len(openPathHexs) != 0:

            # Sorting the open list to get the Hex with the lowest F.
            openPathHexs.sort(key=lambda x: x.F)
            # openPathHexs = openPathHexs.OrderBy(x => x.F).ThenByDescending(x => x.g).ToList()

            # Removing the current Hex from the open list and appending it to the closed list.
            currentHex = openPathHexs.pop(0)
            closedPathHexs.append(currentHex)

            g = currentHex.g + 1

            # If there is a target Hex in the closed list, we have found a path.
            if end_point in closedPathHexs:
                end_point.g = g - 1
                break

            # Investigating each adjacent Hex of the current Hex.
            for adjacentHex in AStarPathfinding.getNeighbourHex(currentHex, end_point):

                # Ignore not walkable adjacent Hexs.
                if adjacentHex in list_exclude_nodes:
                    continue

                # Ignore the Hex if it's already in the closed list.
                if adjacentHex in closedPathHexs:
                    continue

                # If it's not in the open list - append it and compute G and H.
                if adjacentHex not in openPathHexs:
                    adjacentHex.g = g
                    adjacentHex.h = AStarPathfinding.GetEstimatedPathCost(adjacentHex, end_point)
                    adjacentHex.F = adjacentHex.g + adjacentHex.h
                    openPathHexs.append(adjacentHex)

                # Otherwise check if using current G we can get a lower value of F, if so update it's value.
                elif adjacentHex.F > g + adjacentHex.h:
                    adjacentHex.g = g

        finalPathHexs = []

        # Backtracking - setting the final path.
        if end_point in closedPathHexs:
            currentHex = end_point
            i = end_point.g - 1
            while i >= 0:
                # for (int i = endPoint.g - 1 i >= 0 i--)

                # currentHex = closedPathHexs.Find(x => x.g == i && currentHex.adjacentHexs.Contains(x))
                listNeighbours = AStarPathfinding.getNeighbourHexFromClosedPathHexs(currentHex, closedPathHexs)
                listNeighbours.sort(key=lambda x: x.g, reverse=True)
                while len(listNeighbours) > 0:
                    hex_node = listNeighbours.pop(0)
                    if hex_node.g < currentHex.g:
                        finalPathHexs.append(currentHex)
                        currentHex = hex_node
                        i -= 1
                        break

            finalPathHexs.reverse()

        return finalPathHexs

    # <summary>
    # Returns estimated path cost from given start position to target position of hex Hex using Manhattan distance.
    # </summary>
    # <param name="startPosition">Start position.</param>
    # <param name="targetPosition">Destination position.</param>
    @staticmethod
    def GetEstimatedPathCost(start_position: HexNode, target_position: HexNode) -> int:
        return max(abs(start_position.z - target_position.z),
                   max(abs(start_position.x - target_position.x), abs(start_position.y - target_position.y)))

    @staticmethod
    def getNeighbourHex(current_hex, end_point):
        listHexs = []
        listHexs.append(HexNode(current_hex.x - 1, current_hex.y + 1, current_hex.z))
        listHexs.append(HexNode(current_hex.x - 1, current_hex.y, current_hex.z + 1))

        listHexs.append(HexNode(current_hex.x, current_hex.y - 1, current_hex.z + 1))
        listHexs.append(HexNode(current_hex.x + 1, current_hex.y - 1, current_hex.z))

        listHexs.append(HexNode(current_hex.x, current_hex.y + 1, current_hex.z - 1))
        listHexs.append(HexNode(current_hex.x + 1, current_hex.y, current_hex.z - 1))

        if end_point is not None:
            for node in listHexs:
                node.g = current_hex.g + 1
                node.h = AStarPathfinding.GetEstimatedPathCost(node, end_point)
                node.F = node.g + node.h

        return listHexs

    @staticmethod
    def getNeighbourHexFromClosedPathHexs(current_hex, closedPathHexs):
        listHexs = []
        node = next((x for x in closedPathHexs if x == HexNode(current_hex.x - 1, current_hex.y + 1, current_hex.z)), None)
        if node is not None:
            listHexs.append(node)

        node = next((x for x in closedPathHexs if x == HexNode(current_hex.x - 1, current_hex.y, current_hex.z + 1)),
                    None)
        if node is not None:
            listHexs.append(node)

        node = next((x for x in closedPathHexs if x == HexNode(current_hex.x, current_hex.y - 1, current_hex.z + 1)),
                    None)
        if node is not None:
            listHexs.append(node)

        node = next((x for x in closedPathHexs if x == HexNode(current_hex.x + 1, current_hex.y - 1, current_hex.z)),
                    None)
        if node is not None:
            listHexs.append(node)

        node = next((x for x in closedPathHexs if x == HexNode(current_hex.x, current_hex.y + 1, current_hex.z - 1)),
                    None)
        if node is not None:
            listHexs.append(node)

        node = next((x for x in closedPathHexs if x == HexNode(current_hex.x + 1, current_hex.y, current_hex.z - 1)),
                    None)
        if node is not None:
            listHexs.append(node)

        return listHexs


# TEST
start_point = HexNode(7, -4, -3)
end_point = HexNode(0, 0, 0)

print(AStarPathfinding.FindPath(start_point, end_point, [HexNode(6, -4, -2), HexNode(6, -3, -3), HexNode(1, -1, 0)]))
