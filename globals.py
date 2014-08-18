import libtcodpy as libtcod

# map of the current level
level_map = []
# all actors
actors = []
# items on ground
items = []
# features on tiles, such as trees
terrain_features = []
# list of game messages and their colors
game_msgs = []

# libtcod event holders
key_event_structure = libtcod.Key()
mouse_event_structure = libtcod.Mouse()

fov_recompute = True
game_state = "playing"
