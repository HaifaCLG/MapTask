import re
import random
from typing import Union

from bots.rule_based.instructor.engage import engage_next
from bots.rule_based.instructor.template_matchers.template_matcher import TemplateMatcher
from bots.rule_based.instructor.template_matchers.template_matcher_share import TemplateMatcherShare


class GeneralInformation(TemplateMatcher):
    """
    e.g.: 'where should I go now?' -> pick next direction from KB abs’
    e.g.: nav: 'where should I go now?', 'ins': engage question , nav: at /near at/ the X, ins: NEAR matcher'
    """
    def __init__(self, share: TemplateMatcherShare):
        super().__init__(share)

    @staticmethod
    def __is_match(text):
        t = text.lower()
        match = bool(re.match("(.*)(where (to|now))(.*)", t))
        match |= bool(re.match("(where (do|should) i (go|head|need to go))(.*)", t))
        match |= bool(re.match("(now (what| where)?)", t))
        match |= bool(re.match("(where do i go)(.*)", t))
        match |= bool(re.match("(i (do not|don't) know)(.*)", t))
        match |= bool(re.match("(.*)(now?)", t))
        match |= bool(re.match("(ok now (what|where)(.*))", t))
        match |= bool(re.match("(.*)(how to continue?)", t))
        match |= bool(re.match("(.*)(what next?)", t))
        match |= bool(re.match("(.*)(what's next?)", t))
        return match

    def match(self, user_msg, user_state=None) -> Union[list[str], None]:
        if user_state is None:
            return

        if not self.__is_match(user_msg):
            return None

        print('match: general matcher')

        if random.random() > 0.25:
            return self.shared.get_kb_suggestion(self.shared.closest_obj)
        else:
            return [f'ok, {engage_next()}']
