from typing import List

from bots.cs_unit import CodeSwitchStrategyName
from bots.gpt.code_switch_strategies.code_switch_strategy import CodeSwitchStrategy
from bots.models.lang_id_bert import LanguageId
from bots.models.nouns_extractor_spacy import NounsExtractor
import codecs
from collections import Counter


class InsertionalSpanishIncongruent(CodeSwitchStrategy):
    """
        1. Nouns are always translated from ES to ENG
        2. DET (or edge case or ADP) are gender switched according to condition
    """

    def __init__(self, strategy: CodeSwitchStrategyName):
        super().__init__()
        self.metadata = []  # the metadata we save is the bot responses where CS was made

        self.strategy = strategy
        self.strategies = {
            CodeSwitchStrategyName.insertional_spanish_incongruent1: self.__incongruent_1,
            CodeSwitchStrategyName.insertional_spanish_incongruent2: self.__incongruent_2,
            CodeSwitchStrategyName.insertional_spanish_congruent: self.__congruent
        }

        self.noun_phrase_extractor = NounsExtractor()
        nouns_file = codecs.open('bots/gpt/code_switch_strategies/spanish_nouns_set.txt', "r", "utf-8")
        self.es_to_eng_nouns = {n.strip().split('_')[0]: n.strip().split('_')[1] for n in nouns_file.readlines()}

        eng_gender_nouns_file = codecs.open('bots/gpt/code_switch_strategies/english_nouns_gender_set.txt', "r", "utf-8")
        self.eng_gender_nouns = {n.strip().split('_')[0]: n.strip().split('_')[1] for n in eng_gender_nouns_file.readlines()}

        # https://en.wikipedia.org/wiki/Spanish_determiners
        self.masc_femi_determiners_dict = {
            'el': 'la',  # the singular
            'los': 'las',  # the plural
            'ese': 'esa',  # that
            'este': 'esta',  # this
            'esos': 'esas',  # those
            'estos': 'estas',  # those
            'un': 'una',  # a singular
            'unos': 'unas',  # a plural
            'nuestro': 'nuestra',  # my
            'nuestros': 'nuestras',  # ours
            'vuestro': 'vuestra',  # your
            'vuestros': 'vuestras',  # theirs
            #### ADP
            'del': 'de la',  # to the
            'al': 'a la',  # of / to the (al = a + el shortcut)
            ### new:
            'otro': 'otra',
            'otros': 'otras'
        }

    @staticmethod
    def __replace_substrings(text: str, substitutions: list[dict]) -> str:
        substitutions = sorted(substitutions, key=lambda d: d['idx'])
        result = list(text)
        offset = 0

        for sub in substitutions:
            orig_substring = sub['orig']
            switch_substring = sub['new']
            index = sub['idx'] + offset

            result[index:index + len(orig_substring)] = list(switch_substring)
            offset += len(switch_substring) - len(orig_substring)

        return ''.join(result)

    def __swap(self, nouns_bot_resp: list, bot_resp: List[str], det_dict: dict):
        switches = []
        for resp_idx, nouns in enumerate(nouns_bot_resp):
            substitutions = []
            for det, noun in nouns:
                noun_text = noun['text']
                noun_idx = noun['idx']

                det_text = det['text']
                det_idx = det['idx']

                if noun_text not in self.es_to_eng_nouns:
                    continue

                # for in-cong strategies check the det matches the expected gender
                if len(det_dict) and det_text not in det_dict:
                    continue

                translated_noun = self.es_to_eng_nouns[noun_text]
                noun_gender = self.eng_gender_nouns.get(translated_noun, 'amb')
                if noun_gender == 'amb':
                    continue

                switches.append(resp_idx)

                if det_text in det_dict:
                    substitutions.append({'orig': det_text, 'new': det_dict[det_text], 'idx': det_idx})
                    print(f'{resp_idx}:Swapped DET and Noun: {det_text} {noun_text} to: {det_dict[det_text]} {translated_noun}')
                else:
                    print(f'{resp_idx}:Swapped noun only: {noun_text} to: {translated_noun}')

                substitutions.append({'orig': noun_text, 'new': translated_noun, 'idx': noun_idx})

            bot_resp[resp_idx] = self.__replace_substrings(text=bot_resp[resp_idx], substitutions=substitutions)

        for switch in switches:
            self.metadata.append(bot_resp[switch])

    def __congruent(self, nouns_bot_resp: list, bot_resp: List[str]):
        """
        e.g.: el fork/la spoon	i.e. all [Spa] DETs match expected gender
        we assume the gender are fine and don't switch
        """
        self.__swap(nouns_bot_resp, bot_resp, det_dict={})

    def __incongruent_1(self, nouns_bot_resp: list, bot_resp: List[str]):
        """
        e.g.: LA fork/la spoon	i.e. for MASC Ns only, Spanish DET switches genders
        (prediction: increase task times/decrease enjoyment for regular CSers)
        """
        self.__swap(nouns_bot_resp, bot_resp, self.masc_femi_determiners_dict)

    def __incongruent_2(self, nouns_bot_resp: list, bot_resp: List[str]):
        """
        el fork/EL spoon	i.e. for FEM Ns only, Spa DET switches genders
        (prediction: may increase task times/decrease enjoyment for non-CSers, or no effect)
        """
        femi_masc_determiners_dict = {v: k for k, v in self.masc_femi_determiners_dict.items()}
        self.__swap(nouns_bot_resp, bot_resp, femi_masc_determiners_dict)

    @staticmethod
    def __is_valid_spanish_sentence(langs: list[LanguageId]):
        counts = Counter(langs)
        return counts[LanguageId.eng] <= 1

    def call(self, user_msg: str, bot_resp: List[str]) -> tuple[list[str], bool]:
        nouns_bot_resp = []
        for msg in bot_resp:
            langs = self.lid.get_lang_tokens(msg)
            is_spanish = self.__is_valid_spanish_sentence(langs)
            print(is_spanish, msg)
            extracted_nouns = self.noun_phrase_extractor.extract_nouns_with_det(msg,
                                                                                LanguageId.es) if is_spanish else []
            print('extracted_nouns:', extracted_nouns)
            nouns_bot_resp.append(extracted_nouns)

        if not any([len(nouns) for nouns in nouns_bot_resp]):
            return bot_resp, False

        self.strategies[self.strategy](nouns_bot_resp=nouns_bot_resp, bot_resp=bot_resp)

        return bot_resp, False

    def get_game_metadata(self):
        return self.metadata
