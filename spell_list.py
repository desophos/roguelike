from Spell import *
import Effect
from utility import classes_to_dict
import sys


class Immolate(Spell):
    def __init__(self, owner):
        Spell.__init__(self, owner, name="Immolate", power=12, turns=3, mp_cost=5, aspect=aspects[FIRE],
                       desc="Burn an enemy over 3 turns.", effect_verb=['burned'], target_type='enemy', max_range=6,
                       use_classes=[Effect.DamageHP])


class Static(Spell):
    def __init__(self, owner):
        Spell.__init__(self, owner, name="Static bolt", power=5, mp_cost=5, aspect=aspects[AIR],
                       desc="Harness the static electricity in the air to zap the closest enemy.", target_type='closest', max_range=5,
                       use_classes=[Effect.DamageHP])


class WaterJet(Spell):
    def __init__(self, owner):
        Spell.__init__(self, owner, name="Water jet", power=6, mp_cost=7, aspect=aspects[WATER],
                       desc="Condense water from moisture in the air and blast an enemy with it.", target_type='enemy', max_range=6,
                       use_classes=[Effect.DamageHP])


class HealSpell(Spell):
    def __init__(self, owner):
        Spell.__init__(self, owner, name="Heal", power=6, mp_cost=5, aspect=aspects[WATER],
                       desc="Heal some HP.", target_type='self', max_range=1,
                       use_classes=[Effect.HealHP])


class Hold(Spell):
    def __init__(self, owner):
        Spell.__init__(self, owner, name="Hold", power=4, mp_cost=5, aspect=aspects[EARTH],
                       desc="Engulf an enemy's legs with the ground below them, preventing movement.", target_type='enemy', max_range=5,
                       use_classes=[Effect.Hold])


all_spells = classes_to_dict(sys.modules[__name__])
