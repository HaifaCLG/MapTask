import re
from typing import Union
from bots.rule_based.instructor.template_matchers.template_matcher import TemplateMatcher


class Towards(TemplateMatcher):
    """
    e.g. "should I go toward the parrot?" -> yes
    e.g. "should I go toward the parrot?" -> no, <next direction suggestion from abs kb>
    """
    def is_match(self, text):
        t = text.lower()
        for obj_dict in self.shared.all_objects:
            if bool(re.match(f"((.*)(should|do) i (continue to|go towards|go toward|go to|head to|walk to) the {obj_dict['word']}(.*))", t)) or \
                    bool(re.match(f"((.*)(towards|toward) the {obj_dict['word']}(.*))", t)):
                return obj_dict['obj']
        return False

    def match(self, user_msg, user_state=None) -> Union[list[str], None]:
        if user_state is None:
            return None
        obj_match = self.is_match(user_msg)
        if not obj_match:
            return None
        print('match: tow matcher:', obj_match)

        if obj_match == self.shared.goal_object:
            return ['in general yes, but you should follow path instruction']

        closest_obj_index = self.shared.kb_path_order.index(self.shared.closest_obj)
        next_obj_in_path = self.shared.kb_path_order[closest_obj_index + 1]
        if obj_match in self.shared.outside_path:
            return [f'no, the {obj_match} is not part of the path. you should go towards the {next_obj_in_path}']

        obj_match_index = self.shared.kb_path_order.index(obj_match)
        if closest_obj_index == obj_match_index - 1:
            return ['yes']

        elif obj_match_index > closest_obj_index:
            return [f'first you should go towards the {next_obj_in_path}']
        else:
            return [f'nope, you should go towards the {next_obj_in_path}']

