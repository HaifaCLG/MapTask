from typing import Union
from bots.rule_based.instructor.template_matchers.template_matcher import TemplateMatcher
import random
import re
from bots.rule_based.shared_utils import is_basic_greeting, is_how_are_you_greeting

class Greetings(TemplateMatcher):
    basic_options = ['hey there', 'hello there', 'hi', 'hey', 'hello']
    how_are_you_options = ['all well thank you!', 'very well thanks', "i'm good thank you"]
    lets_go_options = ['alright!']

    @staticmethod
    def __is_lets_go(text):
        t = text.lower()
        match = bool(re.match("((let's|lets) (go|start))(.*)", t))
        return match

    def match(self, user_msg, user_state=None) -> Union[list[str], None]:
        if is_how_are_you_greeting(user_msg):
            return [random.choice(Greetings.how_are_you_options)]
        elif is_basic_greeting(user_msg):
            return [random.choice(Greetings.basic_options)]
        elif self.__is_lets_go(user_msg):
            return [random.choice(Greetings.lets_go_options)]
        else:
            return None
