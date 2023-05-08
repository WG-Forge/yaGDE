import pygame
from math import cos, sqrt, pi
from pygame.math import Vector2
from pygame.surface import Surface

from model.common import Content
from model.game import Game
from model.vehicle import Vehicle, VehicleType
from model.hex import Hex, hexes_range

from graphics.utils import (
    even_cuts, 
    hex_center, 
    grouped, 
    hex_size, 
    regular_polygon_corners
)

from graphics.constants import (
    ARROW_WIDTH, 
    CONTENT_COLORS, 
    DRAW_SURFACE_SIZE, 
    PLAYERS_COLORS, 
    SPAWN_COLOR, 
    MOVE_COLOR, 
    SHOOT_COLOR, 
    GRID_COLOR, 
    GRID_WIDTH
)


class HexSurface:
    '''Surface of a single hexagon.'''
    
    def __init__(self, surface: Surface, size: float):
        '''
        <param name="surface">Surface to draw on.</param>
        <param name="size">Size of a hexagon.</param>
        Note: surface is bigger than the hexagon itself
        '''
        
        self.surface = surface
        self.size = size
        self.width = size * 2
        self.height = size * sqrt(3)

    def draw_hex(self, color, width=0):
        '''
        Draws a hexagon with the given color and width.
        
        <param name="color">Color of the hexagon.</param>
        <param name="width">Width of the hexagon.</param>
        '''

        self.draw_regular_polygon(color, 6, width)

    def __regular_polygon_corners(self, sides, factor=1, angle=0):
        '''
        Calculates corners of a regular polygon
        
        <param name="sides">Number of sides of the polygon.</param>
        <param name="factor">Factor to scale the polygon by (relative to self.size).</param>
        <param name="angle">Angle to rotate the polygon by.</param>
        '''
        
        center = self.surface.get_rect().center
        corners = regular_polygon_corners(sides, self.size * factor, angle)

        return [center + point for point in corners]

    def draw_hbar(self, color, vfactor, hfactor, vshift=0, hshift=0):
        center_x, center_y = self.surface.get_rect().center
        width = self.width * hfactor
        height = self.height * vfactor
        vshift = self.height * vshift / 2
        hshift = self.width * hshift / 2
        rect = pygame.Rect(center_x - width / 2 + hshift,
                           center_y - height / 2 + vshift,
                           width, height)

        pygame.draw.rect(self.surface, color, rect)

    def draw_regular_polygon(self, color, sides, width=0, factor=1, angle=0):
        '''
        Draws a regular polygon with the given color and width.
        
        <param name="color">Color of the polygon.</param>
        <param name="sides">Number of sides of the polygon.</param>
        <param name="width">Width of the polygon.</param>
        <param name="factor">Factor to scale the polygon by (relative to self.size).</param>
        <param name="angle">Angle to rotate the polygon by.</param>
        '''

        points = self.__regular_polygon_corners(sides, factor, angle)

        pygame.draw.polygon(self.surface, color, points, width)

    def draw_lined_diamond(self, color, factor=1, num_lines: int = 0):
        '''
        Draws a lined diamond with the given color and width.
        
        <param name="color">Color of the diamond.</param>
        <param name="factor">Factor to scale the diamond by (relative to self.size).</param>
        <param name="num_lines">Number of lines to draw in the diamond.</param>
        '''
        
        points = self.__regular_polygon_corners(4, factor)

        right = even_cuts(points[0], points[1], 2 * num_lines)
        left = even_cuts(points[3], points[2], 2 * num_lines)
        right = grouped(right, 2)
        left = grouped(left, 2)
        for l, r in zip(left, right):
            points = [*l, *reversed(r)]
            pygame.draw.polygon(self.surface, color, points, 0)


class ContentDraw:
    ''' Draws a content on a hexagon.'''

    def __init__(self, surf: HexSurface, content: Content):
        '''
        <param name="surf">Hex Surface to draw on.</param>
        <param name="content">Content to draw.</param>
        '''

        self.surf = surf
        self.content = content

    def draw(self):
        color = CONTENT_COLORS[self.content]
        self.surf.draw_hex(color, 0)


class VehicleDraw:
    '''Draws a vehicle on a hexagon.'''
    
    def __init__(self, surf: HexSurface, vehicle: Vehicle, color):
        '''
        <param name="surf">Hex Surface to draw on.</param>
        <param name="vehicle">Vehicle to draw.</param>
        '''
        
        self.surf = surf
        self.vehicle = vehicle
        self.color = color

    def __draw_symbol(self):
        factor = 0.6
        match self.vehicle.type:
            case VehicleType.LIGHT_TANK:
                self.surf.draw_lined_diamond(
                    self.color, factor=factor, num_lines=0)
            case VehicleType.MEDIUM_TANK:
                self.surf.draw_lined_diamond(
                    self.color, factor=factor, num_lines=1)
            case VehicleType.HEAVY_TANK:
                self.surf.draw_lined_diamond(
                    self.color, factor=factor, num_lines=2)
            case VehicleType.SPG:
                self.surf.draw_regular_polygon(
                    self.color, 4, factor=factor, angle=-pi/4)
            case VehicleType.AT_SPG:
                self.surf.draw_regular_polygon(
                    self.color, 3, factor=factor, angle=-pi/6)
            case _:
                raise ValueError("Unknown vehicle type")

    def __draw_hp(self):
        green = (0, 255, 0)
        red = (255, 0, 0)
        black = (0, 0, 0)

        hfactor = 0.5
        vfactor = 0.15
        vshift = 0.6
        vscale = 0.6
        hscale = 0.9

        scale = self.vehicle.hp / self.vehicle.max_hp

        self.surf.draw_hbar(black, vfactor, hfactor, vshift)
        self.surf.draw_hbar(red, vfactor * vscale, hfactor * hscale, vshift)
        self.surf.draw_hbar(green, vfactor * vscale, hfactor * hscale * scale, vshift,
                            hshift=(1 - scale) * hfactor)

    def draw(self):
        self.__draw_symbol()
        self.__draw_hp()


class Window:
    '''Window to draw the game on.'''
    
    def __init__(self, width, height, title):
        '''
        <param name="width">Width of the window.</param>
        <param name="height">Height of the window.</param>
        <param name="title">Title of the window.</param>
        '''
        
        self.width = width
        self.height = height
        self.title = title
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.surface = pygame.Surface((DRAW_SURFACE_SIZE, DRAW_SURFACE_SIZE),
                                      pygame.SRCALPHA)
        self.hex_size = None

        pygame.display.set_caption(self.title)

    def draw(self, game: Game):
        '''
        Draws the game map on the window.
        
        <param name="game">Game to draw.</param>
        '''

        game_map = game.map
        players_colors = dict(
            # Sort players to insure stable color picking
            zip(sorted(game.players), PLAYERS_COLORS)
        )
        actions = game.actions

        self.hex_size = hex_size(self.surface.get_width() // 5 * 4,
                                 self.surface.get_height() // 5 * 5,
                                 game_map.size)

        self.surface.fill((255, 255, 255))

        # Draw contents
        for hex, content in game_map.contents.items():
            surf = self.__hex_subsurface(hex)
            draw = ContentDraw(surf, content)
            draw.draw()

        # Draw spawns
        for hex in game_map.get_spawn_points():
            surf = self.__hex_subsurface(hex)
            surf.draw_hex(SPAWN_COLOR, 0)

        # Draw grid
        self.__draw_grid(game_map.size)

        # Draw vehicles
        for hex, vehicle in game_map.vehicles.items():
            surf = self.__hex_subsurface(hex)
            draw = VehicleDraw(
                surf, vehicle, players_colors[vehicle.playerId])
            draw.draw()

        # Draw moves
        for move in actions.moves:
            vehicle = game_map.vehicle_by(move.vehicleId)
            self.__draw_arrow(vehicle.position, move.target, MOVE_COLOR)

        # Draw shoots
        for shoot in actions.shoots:
            vehicle = game_map.vehicle_by(shoot.vehicleId)
            self.__draw_arrow(vehicle.position, shoot.target, SHOOT_COLOR)

        self.__flush()

    def __flush(self):
        screen_rect = self.screen.get_rect()
        result_rect = self.surface.get_rect(center=screen_rect.center)

        scale = min(screen_rect.width / result_rect.width,
                    screen_rect.height / result_rect.height)
        result_rect.scale_by_ip(scale)
        result = pygame.transform.smoothscale_by(
            pygame.transform.flip(self.surface, True, False),
            scale)

        self.screen.fill((255, 255, 255))
        self.screen.blit(result, result_rect)

    def update(self):
        '''
        Updates the window.
        This should be called after each draw.
        '''
        
        pygame.display.update()

    def __hex_center(self, hex: Hex) -> Vector2:
        '''
        Calculates the center of a hexagon.
        
        <param name="hex">Hexagon to calculate the center of.</param>
        '''
        
        return hex_center(hex, self.hex_size) + Vector2(self.surface.get_width(), self.surface.get_height()) / 2

    def __hex_subsurface(self, hex: Hex) -> HexSurface:
        '''
        Creates a subsurface for a hexagon.
        
        <param name="hex">Hexagon to create the subsurface for.</param>
        <param name="size">Size of the hexagon.</param>
        '''

        center = self.__hex_center(hex)

        width = self.hex_size * 2
        height = self.hex_size * sqrt(3)

        # Here we add some extra space to the surface to
        # make sure that the hexagon is fully visible.
        delta = 25
        surface = self.surface.subsurface(
            center.x - width / 2 - delta,
            center.y - height / 2 - delta,
            width + 2 * delta,
            height + 2 * delta
        )

        return HexSurface(surface, self.hex_size)

    def __draw_grid(self, map_size: int):
        '''
        Draws the grid on the window.
        
        <param name="map_size">Size of the map.</param>
        '''

        for hex in hexes_range(map_size):
            surf = self.__hex_subsurface(hex)
            surf.draw_hex(GRID_COLOR, GRID_WIDTH)

    def __draw_arrow(self, start: Hex, end: Hex, color):
        '''
        Draws an arrow from one hex to another.
        
        <param name="start">Hex to draw the arrow from.</param>
        <param name="end">Hex to draw the arrow to.</param>
        '''
        
        angle = pi / 4

        back = self.__hex_center(start)
        point = self.__hex_center(end)
        basis = (back - point).normalize() * self.hex_size * 0.5
        right = basis.rotate_rad(angle) + point
        left = basis.rotate_rad(-angle) + point

        pygame.draw.circle(self.surface, color, back, ARROW_WIDTH, 0)
        pygame.draw.line(self.surface, color,
                         back, point + basis * cos(angle) / 2,
                         ARROW_WIDTH)
        pygame.draw.polygon(self.surface, color, [right, left, point])
