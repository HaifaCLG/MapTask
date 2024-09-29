import random
import re
from typing import Union
from bots.rule_based.navigator.template_matchers.template_matcher import TemplateMatcher

class WhNear(TemplateMatcher):
    near_prefix_options = ["i'm near the", "i'm next to the", "i see the"]
    @staticmethod
    def __is_match(text):
        t = text.lower()
        match = bool(re.match("(.*)(what is (in front of|near|next to) you)(.*)", t))
        match |= bool(re.match("(.*)(what do you see)(.*)", t))
        match |= bool(re.match("(.*)(where are you)(.*)", t))
        return match

    def match(self, user_msg) -> Union[list[str], None]:
        if not self.__is_match(user_msg):
            return None

        print('match: wh near matcher:')
        return [self.shared.get_dist_to_next_state_obj()]
