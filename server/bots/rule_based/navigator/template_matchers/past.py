import re
from typing import Union
from bots.rule_based.navigator.template_matchers.template_matcher import TemplateMatcher


class Past(TemplateMatcher):
    def __is_match(self, text):
        t = text.lower()
        for obj_dict in self.shared.all_objects:
            if bool(re.match(f"((.*)(did|have) you (pass|passed|walked|went|go|visited|visit) (by|on|at|through) the {obj_dict['word']}(.*))", t)):
                return obj_dict['obj']
            elif bool(re.match(f"((.*)(did|have) you (pass|passed|visited|visit) the {obj_dict['word']}(.*))", t)):
                return obj_dict['obj']
        return False

    def match(self, user_msg) -> Union[list[str], None]:
        obj_match = self.__is_match(user_msg)
        if not obj_match:
            return None

        print('match: past matcher:', obj_match)

        obj_idx = self.shared.kb_path_order.index(obj_match)
        if obj_idx == self.shared.next_state_idx:
            return ["it's right next to me"]
        elif obj_idx > self.shared.next_state_idx:
            return ['no']
        else:
            return ['yes']
