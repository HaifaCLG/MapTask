from typing import List
import random

from bots.gpt.code_switch_strategies.code_switch_strategy import CodeSwitchStrategy
from bots.models.lang_id_bert import LanguageId


class AlternationRandom(CodeSwitchStrategy):
    """
    translate on the Turn level - i.e.: can translate more than one utterance
    """
    FACTOR = 0.5

    def call(self, user_msg: str, bot_resp: List[str]) -> tuple[list[str], bool]:
        if random.random() > AlternationRandom.FACTOR:
            return bot_resp, False

        bot_langs = [self.lid.identify(msg) for msg in bot_resp]
        if LanguageId.mix in bot_langs:
            return bot_resp, False

        if len(set(bot_langs)) > 1:
            return bot_resp, False

        # either all are Spanish or English
        lang: LanguageId = bot_langs[0]
        translate_cb = self.translate.translate_to_spa if lang == LanguageId.eng else self.translate.translate_to_eng
        bot_resp_translated = [translate_cb(msg) for msg in bot_resp]
        return bot_resp_translated, True
