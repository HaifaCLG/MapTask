from typing import List
from bots.gpt.code_switch_strategies.code_switch_strategy import CodeSwitchStrategy


class Baseline(CodeSwitchStrategy):
    def call(self, user_msg: str, bot_resp: List[str]) -> tuple[list[str], bool]:
        return bot_resp, False
