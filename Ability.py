from Usable import Usable, UsableManager

CHOICE_MENU_WIDTH = 50


class AbilityManager(UsableManager):
    """Contains and manages a dictionary of Abilities.
    Assigned as a component of a Character component."""
    def assign_owner(self, owner):
        #UsableManager.assign_owner(self, owner)
        for key in self.elements.iterkeys():
            ability = self.elements[key]
            ability.use_msg = ability.verb + " " + ability.name + "."

    def choice_menu(self, header, err_msg):
        return UsableManager.choice_menu(
            self, header, err_msg, CHOICE_MENU_WIDTH
        )


class Ability(Usable):
    """Contains attributes and methods that affect the user.
    Each 'use_class' (Effect) of an Ability
    contains attributes and methods that affect the target.
    use_classes is a list of Effects,
    so Abilities may have multiple functionalities/effects."""
    def __init__(self, owner, name, strength=None, turns=1, desc="placeholder",
                 level=0, xp=0, verb="uses", noun=None, use_msg=None,
                 effect_verb=None, target_type=None, max_range=None,
                 use_classes=None):
        self.name = name
        self.description = desc
        self.level = level
        self.xp = xp
        if not noun:
            noun = self.name
        Usable.__init__(self, owner=owner, strength=strength, turns=turns,
                        verb=verb, noun=noun, effect_verb=effect_verb,
                        target_type=target_type, max_range=max_range,
                        use_classes=use_classes)

    def use(self):
        return Usable.use(self)
