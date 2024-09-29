from singleton_decorator import singleton
from enum import Enum
from transformers import pipeline, AutoModelForTokenClassification, AutoTokenizer
import time


class LanguageId(str, Enum):
    mix = "mix"
    eng = "eng"
    es = 'es'


@singleton
class LangIdBert:
    """
    A wrapper around https://huggingface.co/sagorsarker/codeswitch-spaeng-lid-lince
    *** Download the model in advance to model_path ***
    """
    def __init__(self):
        s = time.time()
        model_path = f'bots/models/spaeng-lid-lince'
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForTokenClassification.from_pretrained(model_path)
        self.lid = pipeline('ner', model=self.model, tokenizer=self.tokenizer)
        print('bert init time: ')
        print(time.time() - s)

    @staticmethod
    def __cs_clf_heuristic(langs: list[LanguageId]) -> LanguageId:
        if LanguageId.eng in langs and LanguageId.es in langs:
            return LanguageId.mix
        if LanguageId.eng in langs:
            return LanguageId.eng
        else:
            return LanguageId.es

    def identify(self, user_msg: str) -> LanguageId:
        langs = self.get_lang_tokens(user_msg)
        return self.__cs_clf_heuristic(langs)

    def get_lang_tokens(self, user_msg: str) -> list[LanguageId]:
        result = self.lid(user_msg)
        langs = []
        for r in result:
            lng = r['entity']
            if lng == 'en':
                langs.append(LanguageId.eng)
            elif lng == 'spa':
                langs.append(LanguageId.es)
        return langs
