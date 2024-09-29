import re
from typing import Union
from bots.rule_based.instructor.template_matchers.template_matcher import TemplateMatcher


class Clarification(TemplateMatcher):
    """
    e.g. "i don't understand" -> response with clarification based on last response
    """
    @staticmethod
    def __is_match(text):
        t = text.lower()
        match = bool(re.match("(what|huh|again)(\?|)$", t))
        match |= bool(re.match("(i (don't|didn't|dont|didnt)(.*)(understand|understood|follow|get|got))", t))
        match |= bool(re.match("(can you repeat)", t))
        return match

    def match(self, user_msg, user_state=None) -> Union[list[str], None]:
        if user_state is None:
            return None
        is_match = self.__is_match(user_msg)
        if not is_match:
            return None
        print('match: Clarification matcher')

        if len(self.shared.chat) < 2:
            return None
        last_bot_msg = self.shared.chat[-2]['text'].lower()

        for key_obj in self.shared.kb_abs:
            for idx, next_dir in enumerate(self.shared.kb_abs[key_obj]['next_direction']):
                if last_bot_msg == next_dir or last_bot_msg in next_dir:
                    curr_suggestion = self.shared.kb_abs[key_obj]["clarification"][idx]
                    return [curr_suggestion] if type(curr_suggestion) == str else curr_suggestion

        return None




