from typing import List
from bots.gpt.code_switch_strategies.code_switch_strategy import CodeSwitchStrategy
from bots.models.lang_id_bert import LanguageId


class AlternationAlignLastUser(CodeSwitchStrategy):
    """
    Translates on the Turn level - i.e.: can translate more than one utterance (translate to the user lng)
    """

    def call(self, user_msg: str, bot_resp: List[str]) -> tuple[list[str], bool]:
        user_lng = self.lid.identify(user_msg)
        if user_lng == LanguageId.mix:
            return bot_resp, False

        bot_langs = [self.lid.identify(msg) for msg in bot_resp]
        # user lng == bot lng, no need to translate
        if len(set(bot_langs)) == 1 and user_lng in set(bot_langs):
            return bot_resp, False

        translate_cb = self.translate.translate_to_eng if user_lng == LanguageId.eng else self.translate.translate_to_spa
        bot_resp_translated = [translate_cb(msg) for msg in bot_resp]
        return bot_resp_translated, True
