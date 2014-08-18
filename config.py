from utility import enum

# actual size of the window
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50

CHAR_INFO_WIDTH = 50
#INFO_POPUP_WIDTH = 30

LIMIT_FPS = 20  # 20 frames-per-second maximum

# size of the map
MAP_WIDTH = 80
MAP_HEIGHT = 43


def exp_xp_curve(level):
    # exponential
    from math import exp
    return exp(level) * 5

# character generation values
DEFAULT_SPEED = 10
DEFAULT_XP_CURVE = exp_xp_curve

AIR = 0
WATER = 1
EARTH = 2
FIRE = 3

aspects = ["AIR", "WATER", "EARTH", "FIRE"]  # clockwise from air
# (hot_cold, wet_dry), where hot and wet are positive
factors = [(1,1), (1,-1), (-1,-1), (-1,1)]

tile_types = enum("CAVE_FLOOR", "CAVE_WALL", "GRASS",
                  "SAND", "SHALLOW_WATER", "DEEP_WATER")
