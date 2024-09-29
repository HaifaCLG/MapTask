import re
from typing import Union

from bots.rule_based.instructor.template_matchers.template_matcher import TemplateMatcher


class GameInstructions(TemplateMatcher):
    """
    e.g.: 'what are the dots?' -> ‘the yellow dot is your location...’
    """
    response = ['the yellow dots show the path you traveled on the map',
                'the purple dots are for you to navigate with your mouse device'
                ]

    @staticmethod
    def __is_match(text):
        t = text.lower()
        match = bool(re.match("(.*)((yellow|purple) dots?)(.*)", t))
        match |= bool(re.match("(what are (the|those) dots?)", t))
        match |= bool(re.match("(.*)(yellow and purple dots?)(.*)", t))
        match |= bool(re.match("(.*)(purple and yellow dots?)(.*)", t))
        match |= bool(re.match("(how (do|can) i move(\?|))$", t))

        return match

    def match(self, user_msg, user_state=None) -> Union[list[str], None]:
        if self.__is_match(user_msg):
            return GameInstructions.response
        else:
            return None
