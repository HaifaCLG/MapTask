import json
import os
import re

import pandas as pd
from lingua import Language, LanguageDetectorBuilder
import langid
from codeswitch.codeswitch import LanguageIdentification
from collections import Counter
import codecs

from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, accuracy_score, precision_score
import matplotlib.pyplot as plt
from tqdm import tqdm
import datetime


def clean_endings(token: str):
    if token.endswith(('!', '.', '?', '¿', ',')):
        return token[:len(token) - 1]
    return token


def pred_token_lingua(token: str):
    lang = lingua_detector.detect_language_of(token)
    return 'eng' if lang == Language.ENGLISH else 'es'


def pred_token_langid(text):
    res = langid.classify(text)
    return 'eng' if res[0] == 'en' else 'es'


def cs_clf_heuristic(langs: list):
    if 'eng' in langs and 'es' in langs:
        return 'mix'
    if 'eng' in langs:
        return 'eng'
    if 'es' in langs:
        return 'es'
    return 'none'


def pred_sentence_via_token_lvl(sentence: str, pred_token: callable):
    langs = [pred_token(token) for token in sentence.split(' ')]
    return cs_clf_heuristic(langs)


def pred_sentence_bert(sentence: str):
    # https://huggingface.co/sagorsarker/codeswitch-spaeng-lid-lince
    result = lid.identify(sentence)
    langs = []
    for r in result:
        lng = r['entity']
        if lng == 'en':
            langs.append('eng')
        elif lng == 'spa':
            langs.append('es')
    return cs_clf_heuristic(langs)


def pred_sentence_lingua(sentence: str):
    result = lingua_detector.detect_multiple_languages_of(sentence)
    if len(result) == 1:
        return 'eng' if result[0].language == Language.ENGLISH else 'es'
    else:
        return 'mix'


def __clf_map_task_dataset_uter_lng(uter: str):
    uter = uter.replace('*finished*', '').strip()
    uter = re.sub("(Okay,|Okay.|Okay|Ok,|OK,|ok,|Ok|OK|ok)", '', uter).strip()
    return pred_sentence_bert(uter)


masc_femi_determiners_dict = {
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

eng_determiners = [
    "the",
    "a",
    "an",
    "this",
    "that",
    "these",
    "those",
    "my",
    "your",
    "his",
    "her",
    "its",
    "our",
    "their",
    "mine",
    "yours",
    "hers",
    "ours",
    "theirs",
    "all",
    "every",
    "each",
    "any",
    "some",
    "several",
    "many",
    "few",
    "numerous",
    "one",
    "two",
    "three",
    "half",
    "a third",
    "three-quarters",
    "enough",
    "lots of",
    "plenty of",
    "most",
    "more",
    "less",
    "little",
    "much",
    "none",
    "no",
    "another",
    "other",
    "both",
    "either",
    "neither",
    "which",
    "what",
    "whose",
    "either",
    "neither",
    "both",
    "all",
    "both",
    "half",
    "twice",
    "double",
    "such",
    "what",
    "rather",
    "quite",
    "one",
    "two",
    "three",
    "first",
    "second",
    "third",
    "single",
    "double",
    "triple",
    "half",
    "third",
    "quarter"
]


def __clf_map_task_dataset_uter_cong_switch_per_token(eng_token: str, idx: int, sentence: list[str]):
    if eng_token not in eng_nouns:
        return None

    if idx == 0:
        print(f'{eng_token} in IDX 0')
        return None

    prev_token = sentence[idx - 1].lower()
    if prev_token in eng_determiners:
        return 'NP'

    if prev_token in masc_femi_determiners_dict:
        det_gender = 'masc'
    elif prev_token in set(masc_femi_determiners_dict.values()):
        det_gender = 'fem'
    else:
        return None

    noun_gender = eng_nouns[eng_token]
    if noun_gender == 'amb':
        return f'amb_{det_gender}'

    if noun_gender == 'masc' and det_gender == 'masc':
        return 'cong_masc'
    if noun_gender == 'fem' and det_gender == 'fem':
        return 'cong_fem'
    if noun_gender == 'masc' and det_gender == 'fem':
        return 'incong_masc'  # incong 1

    return 'incong_fem'  # incong 2


def __clf_map_task_dataset_uter_cong_switch_per_det(eng_token: str, idx: int, sentence: list[str]):
    if eng_token not in eng_nouns:
        return None

    if idx == 0:
        print(f'{eng_token} in IDX 0')
        return None

    prev_token = sentence[idx - 1].lower()
    if prev_token in eng_determiners:
        return None

    if prev_token in masc_femi_determiners_dict:
        det_gender = 'masc'
    elif prev_token in set(masc_femi_determiners_dict.values()):
        det_gender = 'fem'
    else:
        print(f'det w/o gender: {prev_token}_{eng_token}')
        return None

    return det_gender


def __clf_map_task_dataset_uter_cong_switch(uter: str, labels='all') -> list[tuple]:
    """
    :return: list of switches per sentences
    """
    __clf_per_token_foo = __clf_map_task_dataset_uter_cong_switch_per_token if labels == 'all' else __clf_map_task_dataset_uter_cong_switch_per_det

    switches = []

    lng_tokens = lid.identify(uter)
    counts = Counter([ele['entity'] for ele in lng_tokens])
    if counts['spa'] < counts['en']:
        return []

    found_by_clf = set()
    eng_tokens = [(ele['word'], idx) for idx, ele in enumerate(lng_tokens) if ele['entity'] == 'en']
    sentence_by_clf = [ele['word'] for ele in lng_tokens]
    for eng_token, idx in eng_tokens:
        label = __clf_per_token_foo(eng_token.lower(), idx, sentence_by_clf)
        if label is not None:
            switches.append((label, eng_token))
            # print('clf', eng_token, label)
            found_by_clf.add(eng_token)

    # fallback: when clf is missing
    sentence_by_split = uter.split(' ')
    sentence_by_split = [clean_endings(token) for token in sentence_by_split]
    eng_tokens = [(token, idx) for idx, token in enumerate(sentence_by_split) if token in eng_nouns]
    for eng_token, idx in eng_tokens:
        if eng_token in found_by_clf:
            continue
        label = __clf_per_token_foo(eng_token, idx, sentence_by_split)
        if label is not None:
            switches.append((label, eng_token))
            # print('basic', eng_token, label)

    return switches


def remove_invalid_incong_data():
    root_folder = r"data/prolific/"
    target_folder = r"data/trash/saturday_invalid_cong"

    for file_name in os.listdir(root_folder):
        json_file = open(os.path.join(root_folder, file_name), encoding='utf8')

        data = json.load(json_file)
        json_file.close()
        version = data['server_version']
        # if version == '2.4.1_p' or version == '2.4.2_p':
        if version == '2.4.0_p':
            source = os.path.join(root_folder, file_name)
            destination = os.path.join(target_folder, file_name)
            os.rename(source, destination)


def clf_map_task_dataset():
    root_folder = r"data/prolific/"
    output_folder = r'data/prolific_lang_ids'

    for file_name in os.listdir(root_folder):
        json_file = open(os.path.join(root_folder, file_name), encoding='utf8')

        if os.path.exists(os.path.join(output_folder, file_name)):
            continue

        data = json.load(json_file)
        json_file.close()
        # only valid data from either ALT or INS experiments
        if data['server_version'] < '2.3.1_p':
            continue

        print(f'do: {file_name}')

        for game in data['games_data']:
            chat = game['chat']
            for chat_ele in chat:
                chat_ele['lang'] = __clf_map_task_dataset_uter_lng(chat_ele['msg'])
                chat_ele['cong_cs'] = __clf_map_task_dataset_uter_cong_switch(chat_ele['msg'], labels='all')
                chat_ele['det_cs'] = __clf_map_task_dataset_uter_cong_switch(chat_ele['msg'], labels='det')

        with open(os.path.join(output_folder, file_name), 'w') as f:
            json.dump(data, f)


def show_examples():
    sents = [

        'Go around the bottom of teh tiger and travel accross to the island with the parrot and elephant',
        'debe empezar',
        'go down al la isla con el snake y ya llegastes',
        'donde empizo',
        'human',
        'car',
        'a car',
        'hi there! que comience el juego!!',  # correct
        'go and make a u-turn',
        'hey, q tal? empezamos el juego?',
        'hi there, empezamos?',
        'hola, q tal? ready to go?',  # mistake
        'si debe empezar at the tent',  # mistake here
        'ok',
        'si',
        'parrot',
        'hello',
        'genial, he llegado a la isla con el tesoro',
    ]

    sents = [
        "Ve con el tiger",
        "ok aqui llegue con el perro",
        "OK ¿y ahora qué?",
        "Ok ¿y ahora qué?",
        "ok, aqui llegue con el perro",
        "OK, ¿y ahora qué?",
        "Ok, ¿y ahora qué?",
        "Ok , ¿y ahora qué?",
        '*finished* gracias por las instrucciones!',
        "Great job! Now, veer slightly left and start heading northwest. Remember to cross between the red tent and the larger speaker. Once you've done that, describe what you see next.",
        "Compra souvenirs en la tienda de regalos",
        'cruza por el stick hacia el tigre',
        "despues tienes que cruzar el alligator"
    ]

    sents = [
        "Okay, i'm at their rear wheel",
        "a la izquierda veo un camino ramificado hacia una isla pequeña con una tiger. ¿cómo debo proceder?",
        "de acuerdo, he llegado a la isla de la parrot",
        " ahora veo una elephant a la izquierda. ¿qué sigue?"
    ]

    # print('token-lvl predication using lingua')
    # for sentence in sents:
    #     print(sentence, '->', pred_sentence_via_token_lvl(sentence, pred_token_lingua).upper())
    # print()
    #
    # print('token-lvl predication using langid')
    # for sentence in sents:
    #     print(sentence, '->', pred_sentence_via_token_lvl(sentence, pred_token_langid).upper())
    # print()
    #
    # print('sentence-lvl predication using lingua')
    # for sentence in sents:
    #     print(sentence, '->', pred_sentence_lingua(sentence).upper())
    # print()

    print('sentence-lvl predication using lince-bert')
    for sentence in sents:
        sent = sentence.replace('*finished*', '').strip()
        sent = re.sub("(Okay,|Okay.|Okay|Ok,|OK,|ok,|Ok|OK|ok)", '', sent).strip()
        print(sentence, '->', pred_sentence_bert(sent).upper())
        ins_cs_label = __clf_map_task_dataset_uter_cong_switch(sent, labels='all')
        print(ins_cs_label)
    print()


def eval_on_custom_dataset():
    def display_and_print(pred, title):
        cm = confusion_matrix(pred, gt, labels=labels)
        disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=labels)
        disp.plot()
        plt.title(title)
        plt.show()

        print(title)
        prec = precision_score(gt, y_pred=pred, average='weighted')
        print(f'accuracy: {accuracy_score(gt, y_pred=pred)}')
        print(f'precision: {prec}')
        print()

    labels = ['eng', 'es', 'mix']
    df = pd.read_csv(r'offline/language/cs_dataset.csv', encoding='utf-8')
    gt = list(df['label'])
    sentences = list(df['text'])

    lingua_token_pred = [pred_sentence_via_token_lvl(sent, pred_token_lingua) for sent in sentences]
    langid_token_pred = [pred_sentence_via_token_lvl(sent, pred_token_langid) for sent in sentences]
    lingua_sent_pred = [pred_sentence_lingua(sent) for sent in sentences]
    bert_linsec_pred = [pred_sentence_bert(sent) for sent in sentences]

    display_and_print(lingua_token_pred, 'lingua token-lvl')
    display_and_print(langid_token_pred, 'langid token-lvl')
    display_and_print(lingua_sent_pred, 'lingua sentence-lvl')
    display_and_print(bert_linsec_pred, 'bert-lince sentence-lvl')

    # explore mistakes
    for idx, y_pred in enumerate(bert_linsec_pred):
        y_true = gt[idx]
        sent = sentences[idx]
        if y_pred != y_true:
            print(f'gt: {y_true} pred: {y_pred} sent: {sent}')

            if y_true == 'eng':
                pred_sentence_bert(sent)


def clf_mb_dataset():
    import pickle
    with open("offline/language/miami_bangor_cs_uters.dat", "rb") as f:
        cs_uters = pickle.load(f)

    for uter in cs_uters:
        ins_clf_labels = __clf_map_task_dataset_uter_cong_switch(uter, labels='all')
        det_labels = __clf_map_task_dataset_uter_cong_switch(uter, labels='det')
        if ins_clf_labels:
            print(uter)
            print()
        if det_labels:
            print(det_labels)


if __name__ == '__main__':
    """
    run from root repo
    """
    # languages = [Language.ENGLISH, Language.SPANISH]
    # lingua_detector = LanguageDetectorBuilder.from_languages(*languages).build()
    # langid.set_languages(['en', 'es'])
    lid = LanguageIdentification('spa-eng')

    nouns_file = codecs.open('offline/nouns/english_nouns_gender_set.txt', "r", "utf-8")
    eng_nouns = {n.strip().split('_')[0]: n.strip().split('_')[1] for n in nouns_file.readlines()}

    # show_examples()
    # eval_on_custom_dataset()
    clf_map_task_dataset()
    # clf_mb_dataset()
