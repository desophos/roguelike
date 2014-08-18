from Item import Item
import Effect
from utility import classes_to_dict
import libtcodpy as libtcod
import sys


class HealingPotion(Item):
    def __init__(self, x, y):
        Item.__init__(self, x, y, '!', 'healing potion', libtcod.violet,
                      strength=10,
                      verb='drinks',
                      use_classes=[Effect.HealHP])


class ManaPotion(Item):
    def __init__(self, x, y):
        Item.__init__(self, x, y, '!', 'mana potion', libtcod.blue,
                      strength=10,
                      verb='drinks',
                      use_classes=[Effect.HealMP])

all_items = classes_to_dict(sys.modules[__name__])
