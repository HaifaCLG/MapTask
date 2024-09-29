from typing import Tuple

from singleton_decorator import singleton
import time
import spacy
from spacy.tokens import Doc, Token

from bots.models.lang_id_bert import LanguageId


@singleton
class NounsExtractor:
    """
    *** Download the models in advance to the path below ***
    """
    def __init__(self):
        s = time.time()
        self.en_nlp = spacy.load(r'bots/models/en_core_web_sm-3.7.1')
        self.es_nlp = spacy.load(r'bots/models/es_core_news_md-3.7.0')
        print('spacy init time: ')
        print(time.time() - s)

    @staticmethod
    def __merge_phrases(doc: Doc):
        with doc.retokenize() as retokenizer:
            for np in list(doc.noun_chunks):
                attrs = {
                    "tag": np.root.tag_,
                    "lemma": np.root.lemma_,
                    "ent_type": np.root.ent_type_,
                }
                retokenizer.merge(np, attrs=attrs)
        return doc

    def extract_nouns_phrases(self, text: str, lang: LanguageId) -> list[str]:
        if lang == LanguageId.mix: return []
        nlp = self.en_nlp if lang == LanguageId.eng else self.es_nlp
        doc = nlp(text)
        doc = self.__merge_phrases(doc)
        return [token.text for token in doc if token.pos_ == 'NOUN']

    @staticmethod
    def __is_complex_noun(noun: Token) -> bool:
        for child in noun.children:
            if child.dep_ in ['amod', 'nmod']:
                print(f'noun: {noun.text} is complex - ignore')
                return True
        return False

    def extract_nouns_with_det(self, text: str, lang: LanguageId) -> list[Tuple[dict, dict]]:
        """
        extracting simple nouns with DET (nouns without DET are ignored, nouns with ADJ / amod edge are ignored)
        valid tuples:
        DET, ..., NOUN
        ADP NOUN (del X, al X)
        ADP, DET,..., NOUN (a la X, de la X)
        """
        if lang == LanguageId.mix: return []
        nlp = self.en_nlp if lang == LanguageId.eng else self.es_nlp
        doc = nlp(text)

        res = []
        for token in doc:
            if token.pos_ != 'NOUN':
                continue

            left_tokens = list(reversed(list(token.lefts)))
            if not left_tokens:
                print(f'no left tokens: {token.text}')
                continue

            det_token = None
            det_token_idx = 0
            for i, left_token in enumerate(left_tokens):
                if left_token.pos_ == 'DET':
                    det_token = left_token
                    det_token_idx = i
                    break

            if det_token is None:
                if left_tokens[0].pos_ == 'ADP' and left_tokens[0].text in ['del', 'al']:
                    det_obj = {'text': left_tokens[0].text, 'idx': left_tokens[0].idx}
                else:
                    print(f'not DET token for: {token.text}')
                    continue
            else:
                if (
                        det_token_idx + 1 < len(left_tokens) and
                        det_token.text == 'la' and
                        left_tokens[det_token_idx + 1].pos_ == 'ADP' and
                        left_tokens[det_token_idx + 1].text in ['a', 'de']
                ):
                    det_obj = {'text': left_tokens[det_token_idx + 1].text + ' la',
                               'idx': left_tokens[det_token_idx + 1].idx}
                else:

                    det_obj = {'text': det_token.text, 'idx': det_token.idx}

            noun_obj = {'text': token.text, 'idx': token.idx}
            if not self.__is_complex_noun(token):
                res.append((det_obj, noun_obj))

        return res


if __name__ == "__main__":
    ex = NounsExtractor()

    texts = [
        'La gerente de la empresa dijo que',
        'al puesto de flores',
        # el perro blanco: blanco is ADJ and not amod on the edge
        'pero no llegues al puesto de flores. dá un giro de 180 grados a la izquierda y cruza de nuevo el sendero hacia el perro blanco. ¿listo?',

        'al tigre en la isla pequeña a mi izquierda.',  # adj with amod edge
        'ya estoy junto al tigre',  # adj but not amod edge

        # basic:
        ' okay, me veo caminando por el camino hacia el tigre',
        '¡genial! ahora estoy en la pequeña isla con el tigre',

        # edge cases
        'voy a la playa',
        'Voy al parque',
        'He pasado el tigre y voy camino del perro y el elefante.',
        'He pasado el tigre y voy camino de la perra y el elefante.',

        # adj
        'la pequeña perra negra fea',
        'el pequeño perro negro feo'
    ]
    for t in texts:
        print(t)
        print(ex.extract_nouns_with_det(t, LanguageId.es))
        print()

