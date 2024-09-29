import re
from typing import Union
from bots.rule_based.navigator.template_matchers.template_matcher import TemplateMatcher


class YnNear(TemplateMatcher):
    def __is_match(self, text):
        t = text.lower()
        for obj_dict in self.shared.all_objects:
            if bool(re.match(f"((.*)(are|do|can) you (near|on|at|next|see) (the|a) {obj_dict['word']}(.*))", t)):
                return obj_dict['obj']
            elif bool(re.match(f"((.*)(are|do) you (next) to (the|a) {obj_dict['word']}(.*))", t)):
                return obj_dict['obj']
        return False

    def match(self, user_msg) -> Union[list[str], None]:
        obj_match = self.__is_match(user_msg)
        if not obj_match:
            return None

        print('match: yn near matcher:', obj_match)

        obj_idx = self.shared.kb_path_order.index(obj_match)
        if obj_idx == self.shared.next_state_idx:
            return ['yes']
        elif obj_idx > self.shared.next_state_idx:
            return self.shared.obj_is_ahead()
        else:
            return self.shared.obj_is_behind(obj_match)
