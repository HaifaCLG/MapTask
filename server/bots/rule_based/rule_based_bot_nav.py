from typing import Tuple
from pkg_resources import resource_filename
from bots.bot import Bot
import json
import random

from bots.cs_unit import CodeSwitchStrategyName
from bots.rule_based.navigator.template_matchers.action import Action
from bots.rule_based.navigator.template_matchers.direction import Direction
from bots.rule_based.navigator.template_matchers.goal import GoalMatcher
from bots.rule_based.navigator.template_matchers.greetings import Greetings
from bots.rule_based.navigator.template_matchers.past import Past
from bots.rule_based.navigator.template_matchers.resp_action import RespAction
from bots.rule_based.navigator.template_matchers.template_matcher_share import TemplateMatcherShare
from bots.rule_based.navigator.template_matchers.wh_near import WhNear
from bots.rule_based.navigator.template_matchers.yn_near import YnNear


class RuleBasedBotNavigator(Bot):
    def __init__(self, map_id):
        super().__init__(CodeSwitchStrategyName.none)
        self.chat = []

        kb_path = resource_filename('bots', f'rule_based/maps_kb/{map_id}.json')
        with open(kb_path, 'r') as f:
            self.kb = json.load(f)

        shared = TemplateMatcherShare(self.kb, self.chat)
        self.shared = shared
        self.ordered_template_matchers = [
            GoalMatcher(shared),
            Greetings(shared),
            YnNear(shared),
            WhNear(shared),
            Past(shared),
            Action(shared),
            RespAction(shared),
            Direction(shared),
        ]

    def default_msg(self):
        prefix_options = ["i'm not sure what you mean",
                          "i didn't quite understand that",
                          "not too sure about that",
                          ]
        prefix = random.choice(prefix_options)
        suffix = random.choice(self.shared.where_to_suffix)
        return [prefix, suffix]

    def __match_and_respond(self, user_msg) -> list[str]:
        try:
            self.shared.update_state()

            user_msg = user_msg.lower()
            if user_msg.endswith(('!', '.')):
                user_msg = user_msg[:len(user_msg) - 1]

            for template_matcher in self.ordered_template_matchers:
                resp = template_matcher.match(user_msg)
                if resp is not None:
                    return resp

            return self.default_msg()

        except Exception as e:
            print('err:', e)

        return self.default_msg()

    def call(self, user_msg, user_state=None) -> Tuple[list[str], bool]:
        self.chat.append({'speaker': 'user', 'text': user_msg})
        bot_msgs = self.__match_and_respond(user_msg)
        bot_msgs = [m.capitalize() for m in bot_msgs]
        for bot_msg in bot_msgs:
            self.chat.append({'speaker': 'bot', 'text': bot_msg})

        is_finish = self.shared.finish
        return bot_msgs, is_finish

    def db_push(self) -> dict:
        return {'rb_nav_state': self.shared.state}

    def db_load(self, data):
        self.shared.state = data['rb_nav_state']
