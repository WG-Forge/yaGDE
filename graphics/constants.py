from model.common import Content


CONTENT_COLORS = {
    Content.BASE: (0, 255, 0, 128),
    Content.OBSTACLE: (0, 0, 0),
    Content.LIGHT_REPAIR: (128, 255, 0, 128),
    Content.HARD_REPAIR: (255, 128, 0, 128),
    Content.CATAPULT: (0, 0, 255, 128)
}


PLAYERS_COLORS = [
    (128, 0, 32),
    (255, 128, 0),
    (0, 128, 128),
    (128, 0, 128),
    (64, 0, 128)
]


SPAWN_COLOR = (255, 128, 64, 128)

GRID_COLOR = (0, 0, 0)
GRID_WIDTH = 5

MOVE_COLOR = (64, 64, 255, 200)
SHOOT_COLOR = (255, 0, 0, 200)
ARROW_WIDTH = 15

DRAW_SURFACE_SIZE = 3840