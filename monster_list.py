from Object import NPC, Combatant
import AI
import inspect
import libtcodpy as libtcod
import sys


class Orc(NPC):
    def __init__(self, x, y):
        NPC.__init__(self, x=x, y=y, char='o', name='orc', color=libtcod.red,
                     combatant = Combatant(hp=10, defense=0, power=3, death_xp=5, death_function=NPC.death),
                     ai = AI.BasicMonster())


class Troll(NPC):
    def __init__(self, x, y):
        NPC.__init__(self, x=x, y=y, char='t', name='troll', color=libtcod.darker_red,
                     combatant = Combatant(hp=16, defense=1, power=4, death_xp=10, death_function=NPC.death),
                     ai = AI.BasicMonster())

current_module = sys.modules[__name__]
# get all classes in this modules, including imported ones
all_classes = inspect.getmembers(current_module, inspect.isclass)
# so all_classes is a list of (name, value) tuples

# get only those classes defined in this module
monsters = []
for i in all_classes:
    if inspect.getmodule(i[1]) == current_module:
        monsters.append(i)

# then dict() that list of tuples to get a dictionary of "Monster":Monster key/value pairs. Bam.
bestiary = dict(monsters)
