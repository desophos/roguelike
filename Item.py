from Usable import Usable, UsableManager
import Object
import display
import globals as g
import libtcodpy as libtcod

INVENTORY_WIDTH = 50


class Inventory(UsableManager):
    """Contains and manages a dictionary of Items.
    Assigned as a component of a Character instance."""
    def assign_owner(self, owner):
        #UsableManager.assign_owner(self, owner)
        for item in self.elements.itervalues():
            item.use_msg = self.owner.name + " uses " + item.name + "."

    def choice_menu(self, key_char):
        print [i.quantity for i in self.elements.values()]
        if key_char == 'd':
            return UsableManager.choice_menu(
                self,
                "Press a letter to drop an item:",
                "Inventory is empty.",
                INVENTORY_WIDTH,
                ["quantity"]
            )
        elif key_char == 'I':
            return UsableManager.choice_menu(
                self,
                "Press a letter to use an item:",
                "Inventory is empty.",
                INVENTORY_WIDTH,
                ["quantity"]
            )

    def add(self, item):
        if item.name not in self.elements.keys():
            UsableManager.add(self, item)
        self.elements[item.name].quantity += 1

    def remove(self, item):
        self.elements[item.name].quantity -= 1
        if self.elements[item.name].quantity <= 0:
            UsableManager.remove(self, item)


class Item(Object.Object, Usable):
    """An item that can be picked up and used.
    The 'use_class' contains attributes and methods that affect the target."""
    def __init__(self, x, y, char, name, color, strength=0, verb='uses',
                 noun=None, use_msg=None, effect_verb=None, target_type='self',
                 max_range=None, use_classes=None):
        Object.Object.__init__(self, x, y, char, name, color)
        noun = 'the ' + self.name
        self.quantity = 0
        Usable.__init__(self, strength=strength, verb=verb, noun=noun,
                        use_msg=use_msg, effect_verb=effect_verb,
                        target_type=target_type, max_range=max_range,
                        use_classes=use_classes)

    def pick_up(self, character):
        # add to player's inventory and remove from the map
        if character == Object.player \
                and len(character.inventory.elements) >= 26:
            display.message('Your inventory is full, cannot pick up ' +
                            self.name + '.', libtcod.red)
        else:
            character.inventory.add(self)
            self.owner = character
            self.targeter.owner = character
            g.items.remove(self)
            if character == Object.player:
                display.message('You picked up a ' +
                                self.name + '!', libtcod.green)

    def drop(self):
        # add to the map and remove from the player's inventory.
        # also, place it at the player's coordinates
        self.owner.inventory.remove(self)
        g.items.append(self)
        self.x = self.owner.x
        self.y = self.owner.y
        if self.owner == Object.player:
            display.message('You dropped a ' + self.name + '.', libtcod.yellow)
        self.owner = None

    def use(self):
        if self.use_classes is None:
            if self.owner == Object.player:
                display.message('The ' + self.name + ' cannot be used.')
        else:
            for effect in self.use_classes:
                effect.strength = self.strength
            result = Usable.use(self)
            if result:
                self.quantity -= 1
                if self.quantity <= 0:
                    # destroy after use, unless it was cancelled for some reason
                    self.owner.inventory.remove(self)
            return result
