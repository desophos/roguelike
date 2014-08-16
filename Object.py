from config import *
from display import message
import Ticker
import display
import globals as g
import libtcodpy as libtcod
import math


class Object:
    #this is a generic object: the player, a monster, an item, the stairs...
    #it's always represented by a character on screen.
    def __init__(self, x, y, char, name, color, blocks=False, blocks_sight=False):
        self.x = x
        self.y = y
        self.char = char
        self.name = name
        self.color = color
        self.blocks = blocks
        self.blocks_sight = blocks_sight

    def move(self, dx, dy):
        move_blocked = False
        x_in_range = True
        y_in_range = True
        if self.x + dx < 0 or self.x + dx >= MAP_WIDTH:
            x_in_range = False
        if self.y + dy < 0 or self.y + dy >= MAP_HEIGHT:
            y_in_range = False

        if x_in_range and y_in_range:
            move_blocked = is_blocked(self.x + dx, self.y + dy)

        # If I am held by a spell or something, I can't move.
        if self.held:
            move_blocked = True

        # Move by the given amount, if the destination is not blocked.
        # Unfortunately, we need a special case for diagonal movement
        # to fix movement along the edge of the map.
        if not move_blocked:
            if dx != 0 and dy != 0:
                if x_in_range and y_in_range:
                    self.x += dx
                    self.y += dy
            elif dx != 0 and x_in_range:
                self.x += dx
            elif dy != 0 and y_in_range:
                self.y += dy

        return not move_blocked

    def move_towards(self, target_x, target_y):
        #vector from this object to the target, and distance
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        #normalize it to length 1 (preserving direction), then round it and
        #convert to integer so the movement is restricted to the map grid
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        self.move(dx, dy)

    def distance_to(self, other):
        #return the distance to another object
        return self.distance(other.x, other.y)

    def distance(self, x, y):
        #return the distance to some coordinates
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    def send_to_back(self):
        #make this object be drawn first, so all others appear above it if they're in the same tile.
        if self in g.actors:
            g.actors.remove(self)
            g.actors.insert(0, self)
        elif self in g.items:
            g.items.remove(self)
            g.items.insert(0, self)

    def draw(self):
        #only show if it's visible to the player
        if libtcod.map_is_in_fov(display.fov_map, self.x, self.y):
            #set the color and then draw the character that represents this object at its position
            libtcod.console_set_default_foreground(display.con, self.color)
            libtcod.console_put_char(display.con, self.x, self.y, self.char, libtcod.BKGND_NONE)

    def clear(self):
        #erase the character that represents this object
        libtcod.console_put_char(display.con, self.x, self.y, ' ', libtcod.BKGND_NONE)


class TerrainFeature(Object):
    def __init__(self, x, y, char, name, color, blocks_sight=False, hot_cold=0, wet_dry=0):
        self.hot_cold = hot_cold
        self.wet_dry = wet_dry
        Object.__init__(self, x, y, char, name, color, blocks=True, blocks_sight=blocks_sight)


class Character(Object):
    def __init__(self, x, y, char, name, color, level=1, xp=0, xp_curve=DEFAULT_XP_CURVE, blocks=True, blocks_sight=False, speed=DEFAULT_SPEED, inventory=None, skills=None,
                 combatant=None, caster=None, ai=None):
        import Item
        import Ability
        self.level = level
        self.xp = xp
        self.xp_curve = xp_curve
        self.held = False
        self.ticker = Ticker.ticker
        self.speed = speed  # speed in ticks
        Ticker.ticker.schedule_turn(self.speed, self)  # schedule first move
        self.inventory = inventory or Item.Inventory(self, {})
        self.skills = skills or Ability.AbilityManager(self, {})

        Object.__init__(self, x=x, y=y, char=char, name=name, color=color, blocks=blocks, blocks_sight=blocks_sight)

        # assign components and tell them their owner

        self.combatant = combatant
        if self.combatant:
            self.combatant.owner = self
        self.caster = caster
        if self.caster:
            self.caster.owner = self
            self.caster.spellbook.assign_owner(self)
        self.ai = ai
        if self.ai:
            self.ai.owner = self

    def level_up(self):
        self.level += 1
        self.xp = 0
        if self.combatant:
            self.combatant.level_up()
        if self.caster:
            self.caster.level_up()

    def do_turn(self):
        if self.xp >= self.xp_curve(self.level):
            self.level_up()
        if libtcod.map_is_in_fov(display.fov_map, self.x, self.y) and self.ai:
            self.ai.do_turn()
        Ticker.ticker.schedule_turn(self.speed, self)


class NPC(Character):
    def __init__(self, x, y, char, name, color, level=1, xp=0, xp_curve=DEFAULT_XP_CURVE, blocks=True, blocks_sight=False, speed=DEFAULT_SPEED, inventory=None, skills=None,
                 combatant=None, caster=None, ai=None):
        Character.__init__(self, x=x, y=y, char=char, name=name, color=color, level=level, xp=xp, xp_curve=xp_curve, blocks=blocks, blocks_sight=blocks_sight, speed=speed, inventory=inventory, skills=skills, combatant=combatant, caster=caster, ai=ai)

    def death(self, killer):
        #transform it into a nasty corpse! it doesn't block, can't be
        #attacked and doesn't move
        Combatant.death(self.combatant, killer)
        self.char = '%'
        self.color = libtcod.dark_red
        self.blocks = False
        self.combatant = None
        self.caster = None
        self.ai = None
        self.name = 'remains of ' + self.name
        self.send_to_back()


class Player(Character):
    def __init__(self, x, y):
        from Spell import SpellBook
        from spell_list import all_spells
        from Skill import SkillManager
        from skill_list import all_skills
        Character.__init__(self, x=x, y=y, char='@', name='player', color=libtcod.white,
                           combatant=Combatant(hp=30, defense=2, power=5, death_function=self.death),
                           caster=Caster(mp=30, hot_cold=0, wet_dry=0))
        player_spellbook = SpellBook(self, all_spells)
        player_skills = SkillManager(self, all_skills)
        self.skills = player_skills
        self.caster.spellbook = player_spellbook

    def level_up(self):
        display.message("You leveled up!", libtcod.light_blue)
        Character.level_up(self)

    def death(self):
        #the game ended!
        message('You died!', libtcod.red)
        g.game_state = 'dead'

        #for added effect, transform the player into a corpse!
        self.char = '%'
        self.color = libtcod.dark_red

    def move_or_attack(self, dx, dy):
        #the coordinates the player is moving to/attacking
        x = self.x + dx
        y = self.y + dy

        #try to find an attackable object there
        target = None
        for actor in g.actors:
            if actor.combatant and actor.x == x and actor.y == y:
                target = actor
                break

        #attack if target found, move otherwise
        if target:
            self.combatant.attack(target)
            return True
        else:
            g.fov_recompute = True
            return self.move(dx, dy)

    def handle_keys(self):
        """Gets and interprets a keypress.
        Possible return values:
        True: player took turn, proceed as normal
        False: player didn't take turn
        'exit': exit game
        """
        libtcod.console_flush()
        libtcod.sys_check_for_event(libtcod.EVENT_ANY, key_event_structure, mouse_event_structure)

        if key_event_structure.vk == libtcod.KEY_ENTER and key_event_structure.lalt:
            #Alt+Enter: toggle fullscreen
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

        elif key_event_structure.vk == libtcod.KEY_ESCAPE:
            return 'exit'  # exit game

        def switch_key(keys):
            return key_event_structure.vk in keys

        if g.game_state is not 'dead':
            #movement keys
            up = [libtcod.KEY_UP, libtcod.KEY_KP8]
            upleft = [libtcod.KEY_KP7]
            left = [libtcod.KEY_LEFT, libtcod.KEY_KP4]
            downleft = [libtcod.KEY_KP1]
            down = [libtcod.KEY_DOWN, libtcod.KEY_KP2]
            downright = [libtcod.KEY_KP3]
            right = [libtcod.KEY_RIGHT, libtcod.KEY_KP6]
            upright = [libtcod.KEY_KP9]
            #other keys
            pickup_key = ['g', ',']
            inventory_key = ['I']
            spellbook_key = ['B']
            skill_key = ['a']
            drop_key = ['d']
            char_screen_key = ['c']

            movement_keys = up + upleft + left + downleft + down + downright + right + upright

            if switch_key(movement_keys):  # player tries to move
                if self.held:
                    print "You're held in place; you can't move."
                    return False  # trying to move shouldn't take a turn if it fails

                if switch_key(up):          return self.move_or_attack(0, -1)
                elif switch_key(upleft):    return self.move_or_attack(-1, -1)
                elif switch_key(left):      return self.move_or_attack(-1, 0)
                elif switch_key(downleft):  return self.move_or_attack(-1, 1)
                elif switch_key(down):      return self.move_or_attack(0, 1)
                elif switch_key(downright): return self.move_or_attack(1, 1)
                elif switch_key(right):     return self.move_or_attack(1, 0)
                elif switch_key(upright):   return self.move_or_attack(1, -1)
            else:
                # test for other keys
                key_char = chr(key_event_structure.c)

                if key_char in pickup_key:
                    # pick up an item
                    for item in g.items:  # look for an item in the player's tile
                        if item.x == self.x and item.y == self.y:
                            item.pick_up(self)
                            break

                if key_char in inventory_key:
                    # show the inventory; if an item is selected, use it
                    chosen_item = self.inventory.choice_menu(key_char)
                    if chosen_item is not None:
                        if chosen_item.use():
                            return True

                if key_char in spellbook_key:
                    # show the list of spells. If a spell is selected, use it.
                    chosen_spell = self.caster.spellbook.choice_menu()
                    if chosen_spell is not None:
                        if (self.caster.mp - chosen_spell.mp_cost) < 0:
                            display.message("You don't have enough MP to cast that spell.", libtcod.pink)
                        else:
                            if self.caster.cast_spell(chosen_spell):
                                return True

                if key_char in skill_key:
                    chosen_skill = self.skills.choice_menu()
                    if chosen_skill is not None:
                        if chosen_skill.use():
                            return True

                if key_char in drop_key:
                    #show the inventory; if an item is selected, drop it
                    chosen_item = self.inventory.choice_menu(key_char)
                    if chosen_item is not None:
                        chosen_item.drop()

                if key_char in char_screen_key:
                    # show the character screen
                    display.char_info_window(self)
                    # wait for keypress
                    libtcod.sys_wait_for_event(libtcod.KEY_PRESSED, key_event_structure, mouse_event_structure, True)

                return False

    def do_turn(self):
        player_action = False
        while not player_action:
            player_action = self.handle_keys()
            display.render_all()
        Character.do_turn(self)
        return player_action


class Combatant:
    # combat-related properties and methods (monster, player, NPC).
    def __init__(self, hp, defense, power, death_xp=0, death_function=None):
        self.max_hp = hp
        self.hp = hp
        self.defense = defense
        self.power = power
        self.death_xp = death_xp
        self.death_function = death_function

    def attack(self, target):
        # a simple formula for attack damage
        damage = self.power - target.combatant.defense

        if damage > 0:
            # make the target take some damage
            message(self.owner.name.capitalize() + ' attacks ' + target.name + ' for ' + str(damage) + ' hit points.')
            target.combatant.change_hp(self.owner, -damage)
        else:
            message(self.owner.name.capitalize() + ' attacks ' + target.name + ' but it has no effect!')

    def change_hp(self, attacker, amount):
        self.hp += amount

        if self.hp > self.max_hp:  # fix this for real later
            self.hp = self.max_hp

        # check for death. if there's a death function, call it
        if self.hp <= 0:
            if self.owner == player:
                player.death()
            else:
                if self.death_function is not None:
                    self.death_function(self.owner, attacker)

    def level_up(self):
        self.max_hp += 5
        pass

    def death(self, killer):
        display.message("The " + self.owner.name + " is dead.", libtcod.orange)
        display.message("The " + killer.name + " gains " + str(self.death_xp) + " XP.", libtcod.light_violet)
        killer.xp += self.death_xp


class Caster:
    # spellcasting-related properties and methods
    def __init__(self, mp=20, hot_cold=0, wet_dry=0, max_factor=10, osmosis_range=0, spellbook=None):
        from Spell import SpellBook
        self.mp = mp
        self.max_mp = mp
        self.base_hot_cold = hot_cold
        self.base_wet_dry = wet_dry
        self.hot_cold = hot_cold
        self.wet_dry = wet_dry
        self.max_factor = max_factor
        self.spellbook = spellbook or SpellBook(self, {})
        self.osmosis_range = osmosis_range

    def change_mp(self, attacker, amount):
        self.mp += amount
        if self.mp < 0:
            self.mp = 0

    def calc_osmosis(self):
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                if self.owner.distance(x, y) <= self.osmosis_range:
                    self.hot_cold += g.level_map[y][x].hot_cold
                    self.wet_dry += g.level_map[y][x].wet_dry
        if self.hot_cold > self.max_factor: self.hot_cold = self.max_factor
        if self.wet_dry  > self.max_factor: self.wet_dry  = self.max_factor

    def reset_factors(self):
        self.hot_cold = self.base_hot_cold
        self.wet_dry = self.base_wet_dry

    def cast_spell(self, spell):
        if (self.mp - spell.mp_cost) < 0:
            return False  # if I don't have enough MP, I can't cast the spell
        self.calc_osmosis()  # calculate the factors from surrounding terrain
        #print self.hot_cold, self.wet_dry
        success = spell.use()
        self.reset_factors()
        if success:
            self.change_mp(self.owner, -spell.mp_cost)
        return success

    def level_up(self):
        self.max_mp += 5


def is_blocked(x, y):
    #first test the map tile
    if g.level_map[y][x].blocked:
        return True

    objects = []
    objects.extend(g.actors)
    objects.extend(g.items)
    objects.extend(g.terrain_features)

    #then check everything in the tile
    for obj in objects:
        if obj.blocks and obj.x == x and obj.y == y:
            return True

    return False


def calc_aspect(hot_cold, wet_dry):
    if hot_cold > 0 and wet_dry > 0:   return aspects[AIR]    # hot and wet
    elif hot_cold < 0 and wet_dry < 0: return aspects[FIRE]   # hot and dry
    elif hot_cold < 0 and wet_dry > 0: return aspects[WATER]  # cold and wet
    elif hot_cold > 0 and wet_dry < 0: return aspects[EARTH]  # cold and dry
    else:                              return None

player = Player(0, 0)
key_event_structure = libtcod.Key()
mouse_event_structure = libtcod.Mouse()
