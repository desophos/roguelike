from Ability import AbilityManager, Ability
from config import *

POWER_SCALING_FACTOR = 0.25


class SpellBook(AbilityManager):
    """Contains and manages a dictionary of Spells.
    Assigned as a component of a Character component.
    Being a component of Caster would make more sense,
    but is inconsistent."""
    def assign_owner(self, owner):
        AbilityManager.assign_owner(self, owner)
        self.recalc_spells()

    def recalc_spells(self):
        for key in self.elements.iterkeys():
            self.elements[key].calc_power()

    def choice_menu(self):
        return AbilityManager.choice_menu(self, "Press a letter to cast a spell:", "You know no spells.")


class Spell(Ability):
    def __init__(self, owner, name, power=0, turns=1, mp_cost=0, aspect=None, desc="", effect_verb=None, target_type=None, max_range=None, use_classes=None):
        self.power = power  # used as base strength
        self.mp_cost = mp_cost
        self.aspect = aspect
        verb = "casts"
        noun = name
        #self.info_to_display = ["Base power: " + str(self.power), "MP cost: " + str(self.mp_cost)]
        Ability.__init__(self, owner=owner, strength=power, turns=turns, name=name, verb=verb, noun=noun, effect_verb=effect_verb, target_type=target_type, max_range=max_range, use_classes=use_classes)

    def power_formula(self, factors):
        power = self.power
        for factor in factors:
            power += factor * POWER_SCALING_FACTOR
        return power

    def calc_power(self):
        caster = self.owner.caster  # Characters own Spells

        if self.aspect == aspects[AIR]:  # hot and wet
            power = self.power_formula([caster.hot_cold, caster.wet_dry])
        elif self.aspect == aspects[WATER]:  # cold and wet
            power = self.power_formula([-caster.hot_cold, caster.wet_dry])
        elif self.aspect == aspects[FIRE]:  # hot and dry
            power = self.power_formula([caster.hot_cold, -caster.wet_dry])
        elif self.aspect == aspects[EARTH]:  # cold and dry
            power = self.power_formula([-caster.hot_cold, -caster.wet_dry])

        if power < 0:
            return 0
        else:
            return power

    def use(self):
        self.strength = self.calc_power()
        return Ability.use(self)
