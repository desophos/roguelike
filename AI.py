import Object
import display
import libtcodpy as libtcod

class BasicMonster:
	#AI for a basic monster.
	def do_turn(self):
		# A basic monster takes its turn.
		monster = self.owner
		# if you can see it, it can see you
		if libtcod.map_is_in_fov(display.fov_map, monster.x, monster.y):
			#move towards player if far away
			if monster.distance_to(Object.player) >= 2:
				monster.move_towards(Object.player.x, Object.player.y)

			#close enough, attack! (if the player is still alive.)
			elif Object.player.combatant.hp > 0: #@UndefinedVariable
				monster.combatant.attack(Object.player)
"""
class ConfusedMonster:
	#AI for a temporarily confused monster (reverts to previous AI after a while).
	def __init__(self, old_ai, num_turns=CONFUSE_NUM_TURNS):
		self.old_ai = old_ai
		self.num_turns = num_turns

	def do_turn(self):
		if self.num_turns > 0:  #still confused...
			#move in a random direction, and decrease the number of turns confused
			self.owner.move(libtcod.random_get_int(0, -1, 1), libtcod.random_get_int(0, -1, 1))
			self.num_turns -= 1

		else:  #restore the previous AI (this one will be deleted because it's not referenced anymore)
			self.owner.ai = self.old_ai
			display.message('The ' + self.owner.name + ' is no longer confused!', libtcod.red)
"""