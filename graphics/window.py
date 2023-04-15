import pygame
from math import *
from pygame.math import Vector2

from model.hex import *
from model.map import GameMap


def hex_size(width: int, height: int, map_size: int) -> float:
    # Calculates the size of a hexagon to fit the given screen exactly.
    #
    # <param name="width">Width of the screen.</param>
    # <param name="height">Height of the screen.</param>
    # <param name="map_size">Size of the map.</param>
    # Note: flat top orientation is assumed

    return min(
        width / (3 * map_size + 2),
        height / (2 * map_size + 1) / sqrt(3)
    )


def hex_center(hex: Hex, size: float) -> Vector2:
    # Calculates the center of the given hexagon with the given size of hex.
    #
    # <param name="hex">Hexagon to calculate the center of.</param>
    # <param name="size">Size of a hexagon.</param>

    e = Vector2(3 / 2, 0)
    f = Vector2(sqrt(3) / 2, sqrt(3))
    coords = Vector2(hex.q, hex.r)

    return Vector2(e.dot(coords), f.dot(coords)) * size


def hex_axes(hex: Hex, size: float) -> list:
    # Calculates the axes of the given hexagon with the given size of hex.
    #
    # <param name="hex">Hexagon to calculate the axes of.</param>
    # <param name="size">Size of a hexagon.</param>
    # Note: flat top orientation is assumed

    center = hex_center(hex, size)
    sides = 6
    angle = 2 * pi / sides

    return [
        center + size * Vector2(cos(angle * i),
                                sin(angle * i))
        for i in range(sides)
    ]


class Window:
    def __init__(self, width, height, title):
        self.width = width
        self.height = height
        self.title = title
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(self.title)

    def draw(self, game_map: GameMap):
        size = hex_size(self.width * 3 // 4,
                        self.height * 3 // 4,
                        game_map.size)

        self.screen.fill((255, 255, 255))
        for hex in hexes_range(game_map.size + 1):
            self.__draw_hex(hex, size)

    def update(self):
        pygame.display.flip()

    def __draw_hex(self, hex: Hex, size: float):
        color = (0, 0, 0)
        thickness = 1
        center = Vector2(self.width / 2, self.height / 2)
        axes = [center + axis for axis in hex_axes(hex, size)]

        pygame.draw.polygon(self.screen, color, axes, thickness)
