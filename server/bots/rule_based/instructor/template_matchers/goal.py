import re
import random
from typing import Union

from bots.rule_based.instructor.template_matchers.template_matcher import TemplateMatcher
from bots.rule_based.shared_utils import is_goal_match


class GoalMatcher(TemplateMatcher):
    """
    e.g.: 'where is the end?' -> ‘the end is some object in the map, you should follow’
    """
    end_response = [['the end is some object on the map', 'you should follow my orders to reach it'],
                    ["the end is some object on the map", "i'll instruct you through"]]
    goal_response = [
        ['the goal is to reach some object on the map in a specific path',
         'you should follow my orders to reach it'],
        ['the goal is to reach some object on the map in a specific path',
         "i'll instruct you through"],
    ]

    @staticmethod
    def __is_end_match(text):
        t = text.lower()
        match = bool(re.match("(.*)((where|what) is the (end))(.*)", t))
        return match


    def match(self, user_msg, user_state=None) -> Union[list[str], None]:
        if self.__is_end_match(user_msg):
            return random.choice(GoalMatcher.end_response)
        elif is_goal_match(user_msg):
            return random.choice(GoalMatcher.goal_response)
        else:
            return None
