from config import MAP_WIDTH, MAP_HEIGHT
import Object
import Ticker
import display
import globals as g
import libtcodpy as libtcod

"""NOTES ON GAMEPLAY:

All player characters are mages
element-based: fire, water, earth, air
Elements are "Aspects" of nature.
Hotness/coldness and wetness/dryness are "Factors" of Aspects.
Terrain-based:
    e.g. standing in water enables certain water-based spells, empowers others
    Casters can absorb energy from the terrain around them to alter their Factors
    Able to change environment to suit your needs
Using a spell of a certain aspect raises the user's proficiency in the factors of that aspect.
This encourages specialization without removing choice.
Player takes a personality test to determine their initial Factors, which determine their initial Aspect.
"""
"""NOTES ON ALCHEMY:

quintessence (aether/void), the fifth element, is incorruptible, unchangeable, non-matter, beyond material world

From Aristotle:
Air is primarily wet and secondarily hot.
Fire is primarily hot and secondarily dry.
Earth is primarily dry and secondarily cold.
Water is primarily cold and secondarily wet.

From Buddha:
Four material properties: solidity, fluidity, temperature, and mobility.
earth: *solidity*/inertia
water: cohesion/*fluidity*
air: expansion/vibration/*mobility*
fire: heat/*energy content*

Humour      Season  Element Organ       Qualities   Ancient name    Modern      MBTI    Ancient characteristics
Blood       spring  air     liver       warm & wet  sanguine        artisan     SP      courageous, hopeful, amorous
Yellow bile summer  fire    gallbladder warm & dry  choleric        idealist    NF      easily angered, bad tempered
Black bile  autumn  earth   spleen      cold & dry  melancholic     guardian    SJ      despondent, sleepless, irritable
Phlegm      winter  water   brain/lungs cold & wet  phlegmatic      rational    NT      calm, unemotional

Historically, bodily problems were caused by an imbalance of the humours.
However, an imbalance of the humours is required for magic.
So mages are prone to bodily problems, i.e. illness. Therefore they are sickly and fragile.
Magic is nature's way of siphoning excess humours.
Unfortunately, this results in the most imbalanced people having the most power, which is extremely dangerous for everyone else.
Aspects might correspond to different types of mental imbalance, i.e. insanity. Exaggerate personality traits?

Use Keirsey's extension of Plato's temperament theory:
http://en.wikipedia.org/wiki/Keirsey_Temperament_Sorter

"""
"""ASPECT COORDINATES:

FIRE    HOT     AIR
         |
DRY -----|----- WET
         |
EARTH   COLD    WATER

Opposite pairs: fire/water, air/earth.
This forces exclusion of only one Aspect.

Earth contains defensive spells and spells that decrease mobility.
Water contains DoT spells, healing spells, and spells that promote consistency and sameness, i.e. dispel and equalizers.
Air contains quick attacks and spells that enhance mobility.
Fire contains offensive spells and those that enhance offensive capabilities.

Water promotes balance, fire promotes imbalance.
Air promotes flexibility, earth promotes stability.

Character roles:

Hot (fire/air):
Dry (fire/earth):
Cold (earth/water):
Wet (air/water):

Sanguine (air):
Choleric (fire):
Melancholic (earth):
Phlegmatic (water):
"""
"""DEVELOPMENT STANDARDS:
Characters own Usables. Usables own Effects. Characters own Targeters, but Effects have targets.
Use keyword arguments to make refactoring easier.
"""
"""TODO:

DON'T FORGET TO TEST AFTER EACH CHANGE!

*: easy
**: needs investigating
***: will take some work
****: difficult
*****: will take significant refactoring
#: work in progress

URGENT (game-breaking):

IMPORTANT (significantly impairs gameplay experience):
**BSP dungeon generation sometimes generates rooms with no connections

NONTRIVIAL (noticeable but has little effect on gameplay):

TRIVIAL (barely noticeable or has no effect on gameplay):
**Don't let player heal self if player has max HP.

CODE ONLY:
*****Improve/generalize User/Targeter/Effect chain
*****All choice_menu() code is hacky.
****Effect.do_turn() is hacky.
*Implement keyword arguments for terrain feature generation

FEATURES TO IMPLEMENT:
**Introductory personality test
***Passive skills
***Spell proficiency
***UsableManager.sort()
***Graphical numerical displays (e.g. hovering XP, damage, etc. amounts over character on map)
***Graphical spell effects
*****Extend Targeter class to be usable by NPCs
**Add choice menu item information
**Multiple dungeon levels
"""


def generate_map(which_kind):
    import map_generator
    if which_kind == "forest":
        map_generator.generate_forest()
        map_generator.generate_river()
        starting_point = (MAP_WIDTH/2, MAP_HEIGHT/2)
        room = map_generator.Room(0, 0, MAP_WIDTH - 1, MAP_HEIGHT - 1)
        map_generator.place_objects(room)
    elif which_kind == "dungeon":
        starting_point = map_generator.generate_dungeon()
    return starting_point

##################
# INITIALIZATION #
##################

# add the player to the global list of objects
g.actors.append(Object.player)

# generate map (at this point it's not drawn to the screen)
Object.player.x, Object.player.y = generate_map("dungeon")

block_map = [[False for x in range(MAP_WIDTH)] for y in range(MAP_HEIGHT)]
block_sight_map = [[False for x in range(MAP_WIDTH)] for y in range(MAP_HEIGHT)]

objects = []
objects.extend(g.actors)
objects.extend(g.items)
objects.extend(g.terrain_features)

for y in range(MAP_HEIGHT):
    for x in range(MAP_WIDTH):
        for obj in objects:
            if obj.x == x and obj.y == y:
                if obj.blocks:
                    block_map[y][x] = True
                if obj.blocks_sight:
                    block_sight_map[y][x] = True
        if g.level_map[y][x].blocked:
            block_map[y][x] = True
        if g.level_map[y][x].block_sight:
            block_sight_map[y][x] = True
        libtcod.map_set_properties(display.fov_map, x, y, not block_sight_map[y][x], not block_map[y][x])

g.fov_recompute = True

g.game_state = 'playing'
player_action = None

#display.message('Fight your way through the forest.', libtcod.red)
display.message('Use the numpad to move.', libtcod.red)
display.message('@ = you, ! = item, o/t = enemy.', libtcod.red)
display.message('get-item: g, drop-item: d, inventory: I, ', libtcod.red)
display.message('spellbook: B, abilities: a', libtcod.red)

#############
# MAIN LOOP #
#############

while not libtcod.console_is_window_closed() and g.game_state is not 'exit':
    # render the screen
    display.render_all()

    # step to next round
    player_action = Ticker.ticker.next_turn()
    if player_action == 'exit':
        g.game_state = 'exit'
