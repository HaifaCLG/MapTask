from typing import List
from bots.gpt.code_switch_strategies.code_switch_strategy import CodeSwitchStrategy
from bots.models.lang_id_bert import LanguageId
from bots.models.nouns_extractor_spacy import NounsExtractor
import codecs

class InsertionalNounPhraseExample(CodeSwitchStrategy):
    """
    This is an example strategy and us used.
    Note: override the bot history (returning True in the call) effect GPT in a way that it start generating
    CS on its own
    """

    def __init__(self):
        super().__init__()
        self.noun_phrase_extractor = NounsExtractor()
        nouns_file = codecs.open('bots/gpt/code_switch_strategies/nouns_set_example.txt', "r", "utf-8")
        self.nouns_set = set([n.strip() for n in nouns_file.readlines()])
        nouns_file.close()

    def call(self, user_msg: str, bot_resp: List[str]) -> tuple[list[str], bool]:
        nouns_bot_resp = []
        bot_langs = []
        for msg in bot_resp:
            bot_lang: LanguageId = self.lid.identify(msg)
            bot_langs.append(bot_lang)
            nouns_bot_resp.append(self.noun_phrase_extractor.extract_nouns_phrases(msg, bot_lang))

        candidates = []
        for resp_idx, nouns_per_resp in enumerate(nouns_bot_resp):
            for np in nouns_per_resp:
                if any([token in self.nouns_set for token in np.split(' ')]):
                    candidates.append((np, resp_idx))

        if not candidates:
            return bot_resp, False

        for selected_np, selected_idx in candidates:
            lang = bot_langs[selected_idx]
            translate_cb = self.translate.translate_to_spa if lang == LanguageId.eng else self.translate.translate_to_eng

            translated_np = translate_cb(selected_np).lower()
            print(f'Translated selected noun phrase: {selected_np} --- to: {translated_np}')

            msg = bot_resp[selected_idx]
            # replace: no need to check if the string is in
            bot_resp[selected_idx] = msg.replace(selected_np, translated_np)

        return bot_resp, True
