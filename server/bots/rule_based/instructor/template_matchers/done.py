import re
import random
from typing import Union

from bots.rule_based.instructor.engage import engage_next
from bots.rule_based.instructor.template_matchers.template_matcher import TemplateMatcher
from bots.rule_based.instructor.template_matchers.template_matcher_share import TemplateMatcherShare


class Done(TemplateMatcher):
    """
    e.g.: nav: 'done', ins: 'awsome, where are you now?', nav: 'at the X', 'ins': NEAR matcher
    """

    def __init__(self, share: TemplateMatcherShare):
        super().__init__(share)
        self.prefix_resp = ['awsome', 'cool', 'nice', 'well done', 'ok']

    @staticmethod
    def __is_match(text):
        t = text.lower()
        match = bool(re.match("((oh |hm |ok )?(ok|okay|cool|done|did it|awsome|got it|sure|nice|sure thing|allright)$)", t))
        match |= bool(re.match("((oh |hm |ok )?(i'm |im |i am )?(there|here|going)$)", t))
        return match

    def match(self, user_msg, user_state=None) -> Union[list[str], None]:
        if user_state is None:
            return

        is_match = self.__is_match(user_msg)
        if not is_match:
            return None

        prefix = random.choice(self.prefix_resp)
        resp_opt = engage_next()
        return [f'{prefix}, {resp_opt}']
