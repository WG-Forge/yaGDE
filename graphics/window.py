import pygame
from math import *
from pygame.math import Vector2
from pygame.surface import Surface

from model.hex import *
from model.map import *
from model.common import *
from model.vehicle import *
from graphics.utils import *


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


def regular_polygon_corners(sides: int, size: float = 1, angle: float = 0) -> list:
    # Calculates corners of a regular polygon with the given size.

    angle_diff = 2 * pi / sides

    return [
        size * Vector2(cos(angle + angle_diff * i),
                       sin(angle + angle_diff * i))
        for i in range(sides)
    ]


def hex_corners(size: float, angle: float = 0) -> list:
    # Calculates corners of a hexagon with the given size.

    return regular_polygon_corners(6, size, angle)


class HexSurface:
    def __init__(self, surface: Surface, size: float):
        self.surface = surface
        self.size = size

    def draw_hex(self, color, width=0):
        self.draw_regular_polygon(color, 6, width)

    def __regular_polygon_corners(self, sides, factor=1, angle=0):
        center = self.surface.get_rect().center
        corners = regular_polygon_corners(sides, self.size * factor, angle)

        return [center + point for point in corners]

    def draw_regular_polygon(self, color, sides, width=0, factor=1, angle=0):
        points = self.__regular_polygon_corners(sides, factor, angle)

        pygame.draw.polygon(self.surface, color, points, width)

    def draw_lined_diamond(self, color, factor=1, num_lines: int = 0):
        points = self.__regular_polygon_corners(4, factor)

        right = even_cuts(points[0], points[1], 2 * num_lines)
        left = even_cuts(points[3], points[2], 2 * num_lines)
        right = grouped(right, 2)
        left = grouped(left, 2)
        for l, r in zip(left, right):
            points = [*l, *reversed(r)]
            pygame.draw.polygon(self.surface, color, points, 0)


CONTENT_COLORS = {
    Content.BASE: (0, 255, 0, 128),
    Content.OBSTACLE: (0, 0, 0),
    Content.LIGHT_REPAIR: (128, 255, 0, 128),
    Content.HARD_REPAIR: (255, 128, 0, 128),
    Content.CATAPULT: (0, 0, 255, 128)
}


class ContentDraw:
    def __init__(self, surf: HexSurface, content: Content):
        self.surf = surf
        self.content = content

    def draw(self):
        color = CONTENT_COLORS[self.content]
        self.surf.draw_hex(color, 0)


class VehicleDraw:
    def __init__(self, surf: HexSurface, vehicle: Vehicle):
        self.surf = surf
        self.vehicle = vehicle

    def draw(self):
        # TODO: Pick color by player id
        color = (255, 0, 0)
        factor = 0.6
        match self.vehicle.type:
            case VehicleType.LIGHT_TANK:
                self.surf.draw_lined_diamond(color, factor=factor, num_lines=0)
            case VehicleType.MEDIUM_TANK:
                self.surf.draw_lined_diamond(color, factor=factor, num_lines=1)
            case VehicleType.HEAVY_TANK:
                self.surf.draw_lined_diamond(color, factor=factor, num_lines=2)
            case VehicleType.SPG:
                self.surf.draw_regular_polygon(
                    color, 4, factor=factor, angle=-pi/4)
            case VehicleType.AT_SPG:
                self.surf.draw_regular_polygon(
                    color, 3, factor=factor, angle=-pi/6)
            case _:
                raise ValueError("Unknown vehicle type")


class Window:
    def __init__(self, width, height, title):
        self.width = width
        self.height = height
        self.title = title
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.hex_size = None
        pygame.display.set_caption(self.title)

    def draw(self, game_map: GameMap):
        self.hex_size = hex_size(self.width * 4 // 5,
                                 self.height * 4 // 5,
                                 game_map.size)

        self.screen.fill((255, 255, 255))

        for hex, content in game_map.contents.items():
            surf = self.__hex_subsurface(hex, self.hex_size)
            draw = ContentDraw(surf, content)
            draw.draw()

        for hex, vehicle in game_map.vehicles.items():
            surf = self.__hex_subsurface(hex, self.hex_size)
            draw = VehicleDraw(surf, vehicle)
            draw.draw()

        self.__draw_grid(game_map.size)

    def update(self):
        pygame.display.update()

    def __hex_center(self, hex: Hex, size: float) -> Vector2:
        return hex_center(hex, size) + Vector2(self.width / 2, self.height / 2)

    def __hex_subsurface(self, hex: Hex, size: float) -> HexSurface:
        center = self.__hex_center(hex, size)
        width = size * 2
        height = size * sqrt(3)

        # Here we add some extra space to the surface to
        # make sure that the hexagon is fully visible.
        delta = 25
        surface = self.screen.subsurface(
            center.x - width / 2 - delta,
            center.y - height / 2 - delta,
            width + 2 * delta,
            height + 2 * delta
        )

        return HexSurface(surface, size)

    def __draw_grid(self, map_size: int):
        color = (0, 0, 0)
        width = 5

        for hex in hexes_range(map_size):
            surf = self.__hex_subsurface(hex, self.hex_size)
            surf.draw_hex(color, width)
