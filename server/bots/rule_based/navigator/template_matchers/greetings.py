from typing import Union
import random
from bots.rule_based.navigator.template_matchers.template_matcher import TemplateMatcher
from bots.rule_based.shared_utils import is_basic_greeting, is_how_are_you_greeting


class Greetings(TemplateMatcher):
    basic_options = ['hey there', 'hello there', 'hi', 'hey', 'hello']
    how_are_you_options = ['all well thank you', 'very well thanks', "i'm good thank you"]

    def match(self, user_msg) -> Union[list[str], None]:
        suffix = random.choice(self.shared.where_to_suffix)
        if is_how_are_you_greeting(user_msg):
            opt = random.choice(Greetings.how_are_you_options)
            return [opt, suffix]
        elif is_basic_greeting(user_msg):
            opt = random.choice(Greetings.basic_options)
            return [opt, suffix]
        else:
            return None
