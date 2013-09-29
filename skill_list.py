from Skill import Skill
import Effect
import sys, inspect

class AbsorbHumours(Skill):
	def __init__(self, owner):
		Skill.__init__(self, owner=owner, name="Absorb Humours",
					desc="Absorb humours from the terrain, influencing your Factors.",
					use_msg="absorbs humours from the terrain.",
					target_type='tile', max_range=owner.caster.osmosis_range,
					use_classes=[Effect.AbsorbHumours])

current_module = sys.modules[__name__]
# get all classes in this modules, including imported ones
all_classes = inspect.getmembers(current_module, inspect.isclass)
# so all_classes is a list of (name, value) tuples

# get only those classes defined in this module
skills = []
for i in all_classes:
	if inspect.getmodule(i[1]) == current_module:
		skills.append(i)

# then dict() that list of tuples to get a dictionary of "Skill":Skill key/value pairs. Bam.
all_skills = dict(skills)
