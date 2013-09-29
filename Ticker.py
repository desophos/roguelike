import globals as g

class Ticker:
	"""
	Simple timer for roguelike games. Ripped shamelessly from:
	http://roguebasin.roguelikedevelopment.org/index.php?title=A_simple_turn_scheduling_system_--_Python_implementation
	Thank you!
	"""

	def __init__(self):
		self.ticks = 0  # current ticks--sys.maxint is 2147483647
		self.schedule = {}  # this is the dict of things to do {ticks: [obj1, obj2, ...], ticks+1: [...], ...}

	def schedule_turn(self, interval, obj):
		self.schedule.setdefault(self.ticks + interval, []).append(obj)

	def next_turn(self):
		import Object
		player_action = True
		things_to_do = []
		
		while not things_to_do: # skip ticks until there is a scheduled action
			things_to_do = self.schedule.pop(self.ticks, [])
			if not things_to_do: self.ticks += 1

		# then do everything else
		for obj in things_to_do:
			if obj is Object.player: player_action = Object.player.do_turn()
			elif g.game_state == 'playing':
				obj.do_turn()

		return player_action

ticker = Ticker()