from Skill import Skill
import Effect
from utility import classes_to_dict
import sys


class AbsorbHumours(Skill):
    def __init__(self, owner):
        Skill.__init__(self, owner=owner, name="Absorb Humours",
                       desc="Absorb humours from the terrain, \
                             influencing your Factors.",
                       use_msg="absorbs humours from the terrain.",
                       target_type='tile', max_range=owner.caster.osmosis_range,
                       use_classes=[Effect.AbsorbHumours])

all_skills = classes_to_dict(sys.modules[__name__])
