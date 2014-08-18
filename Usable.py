from config import *
import display
import libtcodpy as libtcod
from Targeter import Targeter

SPELLBOOK_WIDTH = 50


class Usable:
    def __init__(self, owner=None, strength=None, turns=1, verb="uses",
                 noun="a thing", use_msg=None, effect_verb=None,
                 target_type=None, max_range=None, use_classes=None):
        self.owner = owner
        self.strength = strength
        self.turns = turns  # instant by default
        self.use_msg = use_msg
        self.verb = verb
        self.noun = noun
        self.effect_verb = effect_verb
        self.targeter = Targeter(target_type, max_range)
        self.targeter.owner = owner
        self.use_classes = use_classes
        if use_classes:
            for usage in use_classes:
                    usage.owner = self

    def use(self):
        target = self.targeter.choose_target()
        if not target:
            display.message("Usage cancelled.")
        else:
            if not self.use_msg and self.verb and self.noun:
                self.use_msg = self.verb + " " + self.noun + "."
            if self.use_msg:
                display.message(self.owner.name + " " + self.use_msg)
            for i, usage in enumerate(self.use_classes):
                if self.effect_verb:
                    new_effect_verb = self.effect_verb[i]
                else:
                    new_effect_verb = None
                # initialize the use_class as a new Effect
                new_effect = usage(turns=self.turns, verb=new_effect_verb)
                if self.strength:  # if strength is applicable
                    new_effect.strength = self.strength
                new_effect.target = target
                new_effect.owner = self
                new_effect.init_turn()
        return target


class UsableManager:
    """Contains and manages classes in a dictionary.
    Assigned as a component to a Character."""
    def __init__(self, owner, elements):
        """Takes a dictionary of classes and instantiates them."""

        self.elements = elements
        self.owner = owner

        for key in self.elements.iterkeys():
            # change values from classes to instances
            self.elements[key] = self.elements[key](self.owner)

        for key in self.elements.iterkeys():
            element = self.elements[key]
            element.owner = self.owner
            element.targeter.owner = self.owner

    def add(self, element):
        self.elements[element.name] = element

    def remove(self, element):
        del self.elements[element.name]

    #def sort(self):

    def choice_menu(self, header, err_msg, width, params=[]):
        header += "\n"
        err_msg += "\n"
        ordered_params = []
        if not self.elements:
            options = [err_msg]
        else:
            # correspond the order of params to the order of options
            ordered_elements = [element for element
                                in self.elements.itervalues()]
            options = [element.name for element in ordered_elements]
            for param in params:  # currently supports only one param
                ordered_params = [eval("element."+param) for element
                                  in ordered_elements]
        display.menu(header, options, width, ordered_params)

        key = libtcod.console_wait_for_keypress(True)

        #if key.c == ord('D'):
        #   self.desc_menu(header, err_msg, width)

        #make menu disappear after choice is made
        display.render_all()

        #convert the ASCII code to an index
        index = key.c - ord('a')

        #if something legitimate was chosen, return it
        if index >= 0 and index < len(options):
            if self.elements:
                return self.elements.values()[index]

        return None
