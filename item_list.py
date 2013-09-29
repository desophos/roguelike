from Item import Item
import Effect
import libtcodpy as libtcod
import sys
import inspect

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

current_module = sys.modules[__name__]
# get all classes in this modules, including imported ones
all_classes = inspect.getmembers(current_module, inspect.isclass)
# so all_classes is a list of (name, value) tuples

# get only those classes defined in this module
items = []
for i in all_classes:
	if inspect.getmodule(i[1]) == current_module:
		items.append(i)

# then dict() that list of tuples to get a dictionary of "Item":Item key/value pairs. Bam.
all_items = dict(items)
