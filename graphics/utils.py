from math import sqrt, pi
from pygame.math import Vector2

from model.hex import Hex


def hex_size(width: int, height: int, map_size: int) -> float:
    '''
    Calculates the size of a hexagon to fit the given surface exactly.
    
    <param name="width">Width of the surface.</param>
    <param name="height">Height of the surface.</param>
    <param name="map_size">Size of the map.</param>
    Note: flat top orientation is assumed
    '''

    return min(
        width / (3 * map_size + 2),
        height / (2 * map_size + 1) / sqrt(3)
    )


def hex_center(hex: Hex, size: float) -> Vector2:
    '''
    Calculates the center of the given hexagon with the given size of hex.
    
    <param name="hex">Hexagon to calculate the center of.</param>
    <param name="size">Size of a hexagon.</param>
    '''

    e = Vector2(3 / 2, 0)
    f = Vector2(sqrt(3) / 2, sqrt(3))
    coords = Vector2(hex.q, hex.r)

    return Vector2(e.dot(coords), f.dot(coords)) * size


def regular_polygon_corners(sides: int, size: float = 1, angle: float = 0) -> list:
    '''Calculates corners of a regular polygon with the given size.'''

    angle_diff = 2 * pi / sides
    basis = Vector2(size, 0)

    return [
        basis.rotate_rad(angle + angle_diff * i)
        for i in range(sides)
    ]


def hex_corners(size: float, angle: float = 0) -> list:
    '''Calculates corners of a hexagon with the given size.'''

    return regular_polygon_corners(6, size, angle)


def even_cuts(start, end, n):
    '''Return n evenly spaced cuts between start and end'''
    return [start + (end - start) * i / (n + 1) for i in range(0, n + 2)]


def grouped(l, n):
    '''Group a list into n-sized chunks'''
    return [l[i:i + n] for i in range(0, len(l), n)]
