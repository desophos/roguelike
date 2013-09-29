from config import DEFAULT_SPEED
import Ticker
import display

class Effect:
	"""Base class for implementing targetable effects,
	such as healing, protection, special attacks, etc.
	The target will not be defined until usage.
	Effect strength is defined at usage time in Usable.use()."""
	def __init__(self, turns=0, speed=DEFAULT_SPEED, subject=None, helper='is', verb=None, prep='for', num=None, noun=None):
		self.ticker = Ticker.ticker
		self.target = None
		self.turns = turns
		self.turn_counter = turns
		self.speed = speed
		self.subject = subject
		self.helper_verb = helper
		self.verb = verb
		self.preposition = prep
		self.number = num
		self.noun = noun

	def init_turn(self):
		if self.turn_counter:
			self.ticker.schedule_turn(self.speed, self)
		else:
			self.do_turn()

	def do_turn(self):
		from display import message

		if self.turn_counter:
			self.ticker.schedule_turn(self.speed, self)

		if self.noun == "turns": # update the number of turns left as they elapse
			self.number = self.turn_counter

		if self.target:
			if not self.subject:
				# default subjects:
				# tile: owner name
				# other target type: target name
				if self.owner.targeter.target_type is 'tile':
					self.subject = self.owner.owner.name
				else:
					self.subject = self.target.name
			if self.subject[0:4] != "The ": # quickfix
				self.subject = "The " + self.subject

			self.words = [self.subject, self.helper_verb, self.verb, self.preposition, self.number, self.noun]
			self.use_msg = ""

			for word in self.words:
				if word: self.use_msg += str(word) + " " # add all the words together, separated with spaces
			self.use_msg = self.use_msg[:-1] + "." # remove space at the end and add a full stop

			if self.turn_counter:
				if self.owner.targeter.target_type == 'tile':
					message(self.use_msg)
				else:
					if self.owner.owner.combatant and self.turn_counter:
						message(self.use_msg)

		if not self.turn_counter:
			# additional turn will not be scheduled,
			# because it is already decided that
			# we won't run do_turn() again			
			self.reset()

		self.turn_counter -= 1

	def reset(self): # called when turn_counter runs out, so effect is over
		self.turn_counter = self.turns
		self.target = None

class ChangePoints(Effect):
	"""Changes some point value over some amount of time. Instant by default."""
	def __init__(self, turns=1, speed=DEFAULT_SPEED, verb=None, num=None, noun=None):
		Effect.__init__(self, turns, speed, verb=verb, num=num, noun=noun)
	
	def do_turn(self):
		self.strength = self.strength / self.turns # strength per turn
		if not self.number: self.number = abs(self.strength)
		Effect.do_turn(self)

class ChangeHP(ChangePoints):
	def __init__(self, turns=1, speed=DEFAULT_SPEED, verb=None, num=None):
		ChangePoints.__init__(self, turns=turns, speed=speed, verb=verb, num=num, noun="HP")
		# we don't want to schedule a turn until we actually are used

	def do_turn(self):
		ChangePoints.do_turn(self)

class DamageHP(ChangeHP):
	def __init__(self, turns=1, speed=DEFAULT_SPEED, verb=None, num=None):
		if not verb:
			verb = "damaged"
		ChangeHP.__init__(self, turns=turns, speed=speed, verb=verb, num=num)
		
	def do_turn(self):
		ChangeHP.do_turn(self)
		if self.target:
			if self.target.combatant:
				self.target.combatant.change_hp(self.owner.owner, -self.strength)
		
class HealHP(ChangeHP):
	def __init__(self, turns=1, speed=DEFAULT_SPEED, verb=None, num=None):
		if not verb:
			verb = "healed"
		ChangeHP.__init__(self, turns=turns, speed=speed, verb=verb, num=num)
		
	def do_turn(self):
		ChangeHP.do_turn(self)
		if self.target:
			if self.target.combatant:
				self.target.combatant.change_hp(self.owner.owner, self.strength)

class ChangeMP(ChangePoints):
	def __init__(self, turns=1, speed=DEFAULT_SPEED, verb=None, num=None):
		ChangePoints.__init__(self, turns=turns, speed=speed, verb=verb, num=num, noun="MP")

	def do_turn(self):
		ChangePoints.do_turn(self)

class DamageMP(ChangeMP):
	def __init__(self, turns=1, speed=DEFAULT_SPEED, verb=None, num=None):
		if not verb:
			verb = "damaged"
		ChangeMP.__init__(self, turns=turns, speed=speed, verb=verb, num=num)
		
	def do_turn(self):
		ChangeMP.do_turn(self)
		if self.target:
			if self.target.caster:
				self.target.caster.change_mp(self.owner.owner, -self.strength)
		
class HealMP(ChangeMP):
	def __init__(self, turns=1, speed=DEFAULT_SPEED, verb=None, num=None):
		if not verb:
			verb = "healed"
		ChangeMP.__init__(self, turns=turns, speed=speed, verb=verb, num=num)
		
	def do_turn(self):
		ChangeMP.do_turn(self)
		if self.target:
			if self.target.caster:
				self.target.caster.change_mp(self.owner.owner, self.strength)
	
class Hold(Effect):
	def __init__(self, turns=1, speed=DEFAULT_SPEED, verb=None, noun="turns"):
		if not verb:
			verb = "held"
		Effect.__init__(self, turns=turns, speed=speed, verb=verb, noun=noun)

	def init_turn(self):
		from math import ceil
		self.turns = int(ceil(self.strength))
		self.turn_counter = self.turns
		Effect.init_turn(self)

	def do_turn(self):
		if self.target:
			self.speed = self.target.speed # counts down one turn for each turn the held character takes
			self.target.held = True
		Effect.do_turn(self)

	def reset(self):
		self.target.held = False
		if self.target.combatant: #target still alive
			display.message(self.target.name + " can now move freely.")
		Effect.reset(self)

class AbsorbHumours(Effect):
	def __init__(self, turns=1, verb=None):
		if not verb: verb = "absorbs humours"
		Effect.__init__(self, turns=turns, helper=None, verb=verb, prep="from", noun="the terrain")

	def do_turn(self):
		import globals as g

		Effect.do_turn(self)

		if self.turn_counter:
			user = self.owner.owner.caster
			tile_x, tile_y = self.target
			
			if tile_x:
				hot_cold_gain = g.level_map[tile_y][tile_x].hot_cold
				wet_dry_gain = g.level_map[tile_y][tile_x].wet_dry
	
				if user.base_hot_cold + hot_cold_gain > user.max_factor:
					hot_cold_gain -= (hot_cold_gain - user.max_factor)
				if user.base_wet_dry + wet_dry_gain > user.max_factor:
					wet_dry_gain -= (wet_dry_gain - user.max_factor)
	
				user.base_hot_cold += hot_cold_gain
				user.base_wet_dry += wet_dry_gain
	
				if hot_cold_gain > 0:
					display.message(self.owner.owner.name + " feels " + str(hot_cold_gain) + " degrees warmer.")
				elif hot_cold_gain < 0:
					display.message(self.owner.owner.name + " feels " + str(abs(hot_cold_gain)) + " degrees colder.")
				if wet_dry_gain > 0:
					display.message(self.owner.owner.name + " feels " + str(wet_dry_gain) + "% wetter.")
				elif wet_dry_gain < 0:
					display.message(self.owner.owner.name + " feels " + str(abs(wet_dry_gain)) + "% drier.")
