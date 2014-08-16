from Ability import Ability, AbilityManager


class SkillManager(AbilityManager):
    def choice_menu(self):
        return AbilityManager.choice_menu(self, "Press a letter to use a skill:", "You have no skills.")


class Skill(Ability):
    """Active skill. Does things that spells don't, usually involving terrain."""
    def __init__(self, owner, name, desc, use_msg, target_type, max_range, use_classes):
        Ability.__init__(self, owner=owner, name=name, desc=desc, use_msg=use_msg, target_type=target_type, max_range=max_range, use_classes=use_classes)

    def use(self):
        return Ability.use(self)
