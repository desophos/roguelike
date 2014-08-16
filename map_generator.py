from config import MAP_WIDTH, MAP_HEIGHT, tile_types
import Object
import globals as g
import libtcodpy as libtcod
import random

#parameters for dungeon generator
BSP_RECURSE_LEVEL = 4
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 20
MAX_ROOM_MONSTERS = 3
MAX_ROOM_ITEMS = 1

# modifier for probability of feature being generated in generate_forest()
# 1 is unmodified
FOREST_SPARSENESS = 0.5

# create fbm noise map
noise2d_gen = libtcod.noise_new(2, 0.5, 2.0)
noise_map = [
    [
        libtcod.noise_get_fbm(noise2d_gen, [i / float(MAP_WIDTH), j / float(MAP_HEIGHT)], 32.0)
        for i in range(MAP_WIDTH)
    ] for j in range(MAP_HEIGHT)
]  # map of actual fbm noise values


class Tile:
    # a tile of the map and its properties
    def __init__(self, tile_type):
        self.blocked = False
        self.block_sight = None
        self.type = tile_type

        # all tiles start unexplored
        self.explored = False

        if self.type == tile_types.CAVE_FLOOR:
            self.hot_cold = -1
            self.wet_dry = -1
            self.color_in_FOV = libtcod.light_grey
        elif self.type == tile_types.CAVE_WALL:
            self.hot_cold = -1
            self.wet_dry = -1
            self.blocked = True
            self.color_in_FOV = libtcod.grey
        elif self.type == tile_types.GRASS:
            self.hot_cold = 0
            self.wet_dry = 0
            self.color_in_FOV = libtcod.desaturated_green
        elif self.type == tile_types.SAND:
            self.hot_cold = 2
            self.wet_dry = -2
            self.color_in_FOV = libtcod.light_orange
        elif self.type == tile_types.SHALLOW_WATER:
            self.hot_cold = -4
            self.wet_dry = 5
            self.color_in_FOV = libtcod.light_sky
        elif self.type == tile_types.DEEP_WATER:
            self.hot_cold = -6
            self.wet_dry = 8
            self.blocked = True
            self.block_sight = False
            self.color_in_FOV = libtcod.dark_sky

        # the following assignments depend on assignments in the tile_type tests, so they come after the tests

        # by default, a tile blocks sight if it is blocked and vice versa
        if self.block_sight is None:
            self.block_sight = self.blocked

        # set tile color outside of FOV as desaturated and darker than color in FOV
        hsv = libtcod.color_get_hsv(self.color_in_FOV)  # returns [h,s,v]
        # Colors are passed by reference, so we have to create a whole new Color object.
        self.color_out_FOV = libtcod.Color(self.color_in_FOV.r, self.color_in_FOV.g, self.color_in_FOV.b)
        libtcod.color_set_hsv(self.color_out_FOV, hsv[0], hsv[1] / 4, hsv[2] / 4)  # Desaturate and darken color (unseen by default)


def generate_forest():
    # level_map and terrain_features are intentionally local
    from Object import TerrainFeature
    #terrain_features = []
    forest_noise = [[0 for x in range(MAP_WIDTH)] for y in range(MAP_HEIGHT)]

    # make every tile grass
    g.level_map = [[Tile(tile_types.GRASS) for x in range(MAP_WIDTH)] for y in range(MAP_HEIGHT)]

    for i in range(MAP_HEIGHT):
        forest_noise[i] = map(lambda x: (1+x)/2, noise_map[i])  # expressed as percentage of maximum
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            p = random.random()
            if p < float(FOREST_SPARSENESS * forest_noise[y][x]):
                g.terrain_features.append(TerrainFeature(x, y, 'T', 'tree', libtcod.darkest_green, blocks_sight=True))


def generate_river():
    river_start_x = 0
    river_start_y = 0
    river_end_x = MAP_WIDTH - 1
    river_end_y = MAP_HEIGHT - 1

    river_noise = [[0 for y in range(MAP_WIDTH)] for x in range(MAP_HEIGHT)]

    for i in range(MAP_HEIGHT):
        river_noise[i] = map(lambda a: (2+a)**4, noise_map[i])  # scaled up

    def river_cost(xFrom, yFrom, xTo, yTo, river_noise):
        return river_noise[yTo][xTo]

    path = libtcod.path_new_using_function(MAP_WIDTH, MAP_HEIGHT, river_cost, river_noise)
    # wish I could just use (lambda xFrom, yFrom, xTo, yTo, river_noise: river_noise[xTo][yTo])
    libtcod.path_compute(path, river_start_x, river_start_y, river_end_x, river_end_y)

    while not libtcod.path_is_empty(path):
        x, y = libtcod.path_walk(path, True)
        g.level_map[y][x] = Tile(tile_types.SHALLOW_WATER)
        # make a wider river by making all the neighbors water

        # we need to initialize these separately, but I don't know why
        x_in_min = False
        x_in_max = False
        y_in_min = False
        y_in_max = False

        if x-1 >= 0:          x_in_min = True
        if x+1 <  MAP_WIDTH:  x_in_max = True
        if y-1 >= 0:          y_in_min = True
        if y+1 <  MAP_HEIGHT: y_in_max = True
        # left
        if x_in_min:
            g.level_map[y][x-1] = Tile(tile_types.SHALLOW_WATER)
            # bottom left
            if y_in_min:
                g.level_map[y-1][x-1] = Tile(tile_types.SHALLOW_WATER)
            # top left
            if y_in_max:
                g.level_map[y+1][x-1] = Tile(tile_types.SHALLOW_WATER)
        # right
        if x_in_max:
            g.level_map[y][x+1] = Tile(tile_types.SHALLOW_WATER)
            # bottom right
            if y_in_min:
                g.level_map[y-1][x+1] = Tile(tile_types.SHALLOW_WATER)
            # top right
            if y_in_max:
                g.level_map[y+1][x+1] = Tile(tile_types.SHALLOW_WATER)
        # bottom
        if y_in_min:
            g.level_map[y-1][x] = Tile(tile_types.SHALLOW_WATER)
        # top
        if y_in_max:
            g.level_map[y+1][x] = Tile(tile_types.SHALLOW_WATER)

    # Iterate through all the tiles. Remove trees on shallow water tiles.
    for j in range(MAP_HEIGHT):
        for i in range(MAP_WIDTH):
            if g.level_map[j][i].type == tile_types.SHALLOW_WATER:
                for feature in g.terrain_features:
                    if feature.x == i and feature.y == j:
                        g.terrain_features.remove(feature)

    # Iterating through the features instead of the tiles is more efficient,
    # but it doesn't work because I alter the array as I iterate through it.
    # Only some of the trees on water are removed.
#   for feature in terrain_features:
#       if level_map[feature.y][feature.x].type == tile_types.SHALLOW_WATER:
#           print "Removing tree at ",feature.x,",",feature.y
#           terrain_features.remove(feature)

#implement cellular automata for underground areas


class Room:
    #a rectangle on the map, used to characterize a room.
    def __init__(self, x, y, w, h, bsp_level=0):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h
        self.bsp_level = bsp_level

    def center(self):
        center_x = (self.x1 + self.x2) / 2
        center_y = (self.y1 + self.y2) / 2
        return (center_x, center_y)

    def intersect(self, other):
        #returns true if this rectangle intersects with another one
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)


#"""not using this BSP code for now because it doesn't work...


def create_h_tunnel(x1, x2, y):
    #global level_map
    #horizontal tunnel. min() and max() are used in case x1>x2
    for x in range(min(x1, x2), max(x1, x2) + 1):
        g.level_map[y][x] = Tile(tile_types.CAVE_FLOOR)


def create_v_tunnel(y1, y2, x):
    #global level_map
    #vertical tunnel
    for y in range(min(y1, y2), max(y1, y2) + 1):
        g.level_map[y][x] = Tile(tile_types.CAVE_FLOOR)


def generate_dungeon():
    global rooms
    #fill map with "blocked" tiles
    g.level_map = [
        [
            Tile(tile_types.CAVE_WALL)
            for x in range(MAP_WIDTH)
        ]
        for y in range(MAP_HEIGHT)
    ]

    # First, we create the root node of the tree. This node encompasses the whole rectangular region.
    # bsp_new_with_size(x,y,w,h)
    my_bsp = libtcod.bsp_new_with_size(0, 0, MAP_WIDTH - 1, MAP_HEIGHT - 1)

    # Once we have the root node, we split it into smaller non-overlapping nodes.
    # bsp_split_recursive(node, randomizer, num_recursive_levels, minHSize, minVSize, maxHRatio, maxVRatio)
    libtcod.bsp_split_recursive(my_bsp, 0, BSP_RECURSE_LEVEL, ROOM_MIN_SIZE, ROOM_MIN_SIZE, 1.5, 1.5)

    # Then we change each leaf to a room and connect each subdivision with tunnels.
    libtcod.bsp_traverse_inverted_level_order(my_bsp, bsp_leaf_create_room)
    libtcod.bsp_traverse_level_order(my_bsp, bsp_leaf_create_tunnel)

    # set player coordinates to the center of this first room
    return (rooms[0].center()[0], rooms[0].center()[1])
    #player.x = MAP_WIDTH/2
    #player.y = MAP_HEIGHT/2

    # set stairs coordinates to center of last room


def bsp_leaf_create_room(node, data):
    global rooms

    # We want only the leaves.
    # Since we are traversing in inverted-level-order,
    # we have traversed all the leaves once we get to the first non-leaf node.
    if not libtcod.bsp_is_leaf(node):
        return False

    # Otherwise, resize the leaf to the room size.

    # random width and height within leaf size
    new_w = libtcod.random_get_int(0, ROOM_MIN_SIZE, node.w)
    new_h = libtcod.random_get_int(0, ROOM_MIN_SIZE, node.h)

    # random position without going out of the boundaries of the leaf
    new_x = libtcod.random_get_int(0, node.x, node.x + node.w - new_w)
    new_y = libtcod.random_get_int(0, node.y, node.y + node.h - new_h)

    # "Rect" class makes rectangles easier to work with
    new_room = Room(new_x, new_y, new_w, new_h)

    # append the new room to the list of rooms
    # if this is the first room (rooms doesn't exist), create rooms = [new_room]
    try:
        rooms.append(new_room)
    except NameError:
        rooms = [new_room]

    # We don't need to test for intersection because each leaf contains exactly one room.

    # "paint" the room to the map's tiles
    # go through the tiles in the rectangle and make them passable
    for x in range(new_room.x1 + 1, new_room.x2):
        for y in range(new_room.y1 + 1, new_room.y2):
            g.level_map[y][x] = Tile(tile_types.CAVE_FLOOR)

    # add some contents to this room, such as monsters
    place_objects(new_room)

    return True


def room_center(room):
    center_x = (room.x + room.x + room.w) / 2
    center_y = (room.y + room.y + room.h) / 2
    return (center_x, center_y)


def bsp_leaf_create_tunnel(node, data):
    # connect each pair of subdivisions with a tunnel

    if not libtcod.bsp_is_leaf(node):
        # center coordinates of left child
        (left_x, left_y) = room_center(libtcod.bsp_left(node))

        # center coordinates of right child
        (right_x, right_y) = room_center(libtcod.bsp_right(node))

        # flip a coin (random number that is either 0 or 1)
        if libtcod.random_get_int(0, 0, 1) == 1:
            # first move horizontally, then vertically
            create_h_tunnel(left_x, right_x, left_y)
            create_v_tunnel(left_y, right_y, right_x)
        else:
            # first move vertically, then horizontally
            create_v_tunnel(left_y, right_y, left_x)
            create_h_tunnel(left_x, right_x, right_y)

    return True


def place_objects(room):
    from monster_list import bestiary  # make sure we don't accidentally change these
    from item_list import all_items

    #choose random number of monsters
    num_monsters = libtcod.random_get_int(0, 0, MAX_ROOM_MONSTERS)

    for i in range(num_monsters):
        #choose random spot for this monster
        x = libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
        y = libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1)

        #only place it if the tile is not blocked
        if not Object.is_blocked(x, y):
            if libtcod.random_get_int(0, 0, 100) < 80:  # 80% chance of getting an orc
                #create an orc
                monster = bestiary["Orc"](x=x, y=y)
            else:
                #create a troll
                monster = bestiary["Troll"](x=x, y=y)

            g.actors.append(monster)

    #choose random number of items
    num_items = libtcod.random_get_int(0, 0, MAX_ROOM_ITEMS)

    for i in range(num_items):
        #choose random spot for this item
        x = libtcod.random_get_int(0, room.x1 + 1, room.x2 - 1)
        y = libtcod.random_get_int(0, room.y1 + 1, room.y2 - 1)

        #only place it if the tile is not blocked
        if not Object.is_blocked(x, y):
            dice = libtcod.random_get_int(0, 0, 100)
            if dice < 50:
                #create a healing potion (50% chance)
                item = all_items["HealingPotion"](x, y)
            else:
                # create a mana potion (50% chance)
                item = all_items["ManaPotion"](x, y)

            g.items.append(item)
            item.send_to_back()  # items appear below other objects
