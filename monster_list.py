from Object import NPC, Combatant
from utility import classes_to_dict
import AI
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

bestiary = classes_to_dict(sys.modules[__name__])
