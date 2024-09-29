import random
from typing import Union
from bots.rule_based.navigator.template_matchers.template_matcher import TemplateMatcher
from bots.rule_based.shared_utils import is_goal_match


class GoalMatcher(TemplateMatcher):
    goal_response ='you should instruct me with directions (a path from ✕ to ✓)'

    def match(self, user_msg) -> Union[list[str], None]:
        if is_goal_match(user_msg):
            suffix = random.choice(self.shared.where_to_suffix)
            return [GoalMatcher.goal_response, suffix]
        else:
            return None
