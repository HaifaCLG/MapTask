import random
import re
from typing import Union
from bots.rule_based.navigator.template_matchers.template_matcher import TemplateMatcher


class RespAction(TemplateMatcher):
    @staticmethod
    def __is_match(text):
        t = text.lower()
        match = bool(re.match("(.*)(do|go) (it|there|then|to)(.*)", t))
        match |= bool(re.match("so go", t))
        return match

    def match(self, user_msg) -> Union[list[str], None]:
        if not self.__is_match(user_msg):
            return None

        print('match: resp action matcher')

        if len(self.shared.chat) < 2:
            return None
        last_bot_msg = self.shared.chat[-2]['text'].lower()
        if not last_bot_msg.endswith('yet'):
            return None

        self.shared.advance_state_path_idx(1)
        prefix = random.choice(self.shared.moved_prefix)
        return [f'{prefix} {self.shared.next_state_obj}']