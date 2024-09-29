from typing import List
from bots.gpt.code_switch_strategies.code_switch_strategy import CodeSwitchStrategy
from bots.models.lang_id_bert import LanguageId


class AlternationShortContext(CodeSwitchStrategy):
    """
    translate on the utterance lvl - Translate only last one in the turn
    """
    SHORT_CTX = 3

    def __init__(self, welcome_str: str):
        super().__init__()
        self.cs_history: list[LanguageId] = [self.lid.identify(welcome_str)]

    def call(self, user_msg: str, bot_resp: List[str]) -> tuple[list[str], bool]:
        bot_langs = [self.lid.identify(msg) for msg in bot_resp]
        self.cs_history.extend(bot_langs)

        if len(self.cs_history) < AlternationShortContext.SHORT_CTX:
            return bot_resp, False

        if self.cs_history[-1] == LanguageId.mix:
            return bot_resp, False

        last_langs = self.cs_history[-AlternationShortContext.SHORT_CTX:]
        last_langs_set = set(last_langs)
        if LanguageId.mix in last_langs_set:
            last_langs_set.remove(LanguageId.mix)
        if len(last_langs_set) > 1:
            return bot_resp, False

        lang = self.cs_history[-1]
        translate_cb = self.translate.translate_to_spa if lang == LanguageId.eng else self.translate.translate_to_eng

        switch_lang = LanguageId.es if lang == LanguageId.eng else LanguageId.eng
        self.cs_history[-1] = switch_lang

        last_resp = bot_resp[-1]
        bot_resp[-1] = translate_cb(last_resp)

        return bot_resp, True
