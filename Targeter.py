import display
import libtcodpy as libtcod
import globals as g


class Targeter:
    def __init__(self, target_type, max_range):
        target_types = {
            "tile":    (self.target_tile, "Click a tile to target."),
            "enemy":   (self.target_enemy, "Click an enemy to target."),
            "closest": (self.target_closest, None),
            "self":    (self.target_self, None)
        }
        self.target_type = target_type
        self.target_fn = target_types[target_type][0]
        self.target_msg = target_types[target_type][1]
        self.max_range = max_range

    def choose_target(self):
        # generic target function that handles targeting messages
        if self.target_msg is not None:
            display.message(self.target_msg)
        return self.target_fn()

    def target_enemy(self):
        # returns a clicked enemy inside FOV up to a range, or None if right-clicked
        #display.message("Click an enemy to target.")
        while True:
            t = self.target_tile()
            if t is None:  # player cancelled
                return None
            else:
                (x,y) = t
            #return the first clicked monster, otherwise continue looping
            for obj in g.actors:
                if obj.x == x and obj.y == y and obj.combatant and obj != self.owner:
                    return obj

    def target_tile(self):
        # return the position of a tile left-clicked in player's FOV (optionally in a range), or None if right-clicked.
        #display.message("Click a tile to target.")
        while True:
            #libtcod.console_flush()
            libtcod.sys_check_for_event(libtcod.EVENT_ANY, g.key_event_structure, g.mouse_event_structure)
            # render the screen. this erases the inventory and shows the names of objects under the mouse.
            display.render_all()

            (x, y) = (g.mouse_event_structure.cx, g.mouse_event_structure.cy)

            if g.mouse_event_structure.rbutton_pressed or g.key_event_structure.vk == libtcod.KEY_ESCAPE:
                return None  # cancel if the player right-clicked or pressed Escape

            #accept the target if the player clicked in FOV, and in case a range is specified, if it's in that range
            if g.mouse_event_structure.lbutton_pressed:
                if libtcod.map_is_in_fov(display.fov_map, x, y) and (self.max_range is None or self.owner.distance(x, y) <= self.max_range):
                    return (x, y)
                else:
                    display.message("Out of range.")

    def target_closest(self):
        #find closest enemy, up to a maximum range, and in the character's FOV
        closest_enemy = None
        closest_dist = self.max_range + 1  # start with (slightly more than) maximum range

        for obj in g.actors:
            if obj.combatant and not obj == self.owner and libtcod.map_is_in_fov(display.fov_map, obj.x, obj.y):
                #calculate distance between this object and the character
                dist = self.owner.distance_to(obj)
                if dist < closest_dist:  # it's closer, so remember it
                    closest_enemy = obj
                    closest_dist = dist
        if closest_enemy is None:  # and self.owner == player:
            display.message("No enemy in range.")
        return closest_enemy

    def target_self(self):
        return self.owner
