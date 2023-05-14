import unittest
from itertools import *

from ai.pathFinder import *


class DeserializeTestCase(unittest.TestCase):
    def check_path(self, path, start, end, excluded={}):
        self.assertTrue(path)
        self.assertEqual(path[0], start)
        self.assertEqual(path[-1], end)
        prev = start
        for hex in path[1:]:
            self.assertNotIn(hex, excluded)
            self.assertEqual(hex.distance(prev), 1)
            prev = hex

    def test_basic_path(self):
        size = 4
        center = Hex(0, 0, 0)
        finder = AStarPathfinding(size, center)

        for start, end in permutations(center.range(size), 2):
            path = finder.path(start, end, {}, 1)
            self.assertEqual(len(path), start.distance(end) + 1)
            self.check_path(path, start, end)

    def test_path_with_obstacles_lines(self):
        size = 4
        center = Hex(0, 0, 0)
        finder = AStarPathfinding(size, center)

        # Two parallel lines next to center
        excluded = {
            Hex(1, i, -1 - i) for i in range(-2, 2)
        }.union({
            Hex(-1, i, 1 - i) for i in range(-2, 2)
        })
        for start, end in permutations(center.range(size), 2):
            if start in excluded or end in excluded:
                continue
            result = finder.path(start, end, excluded, 1)\
                # Path is longer by 5 in the worst case
            self.assertLessEqual(len(result), start.distance(end) + 5)
            self.check_path(result, start, end, excluded)

    def test_non_existent_path(self):
        size = 6
        center = Hex(0, 0, 0)
        finder = AStarPathfinding(size, center)

        # Sphere around center
        excluded = set(center.range(2, 3))
        for start, end in product(center.range(2), center.range(3, size + 1)):
            result = finder.path(start, end, excluded, 1)
            self.assertFalse(result)
