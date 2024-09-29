import os
import json
import stanza
import nltk
from tqdm import tqdm

from app.pages.common.versions import experiments_short_names, root_folder
import pandas as pd

experiments = ['Baseline', 'Random CS', 'Short-context CS', 'Adversarial CS', 'Alignment CS']

def __is_eng_noun_exist(root):
    if type(root) != nltk.tree.Tree:
        return False
    if root.label() in ['NN', 'NNS', 'NNP']:
        return True
    for idx, child in enumerate(root):
        if __is_eng_noun_exist(child):
            return True
    return False


def __is_eng_valid_np(root):
    if type(root) != nltk.tree.Tree:
        return False
    if root.label() != 'NP':
        return False
    return __is_eng_noun_exist(root)


def extract_english_noun_phrases_aux(root, nouns):
    if type(root) != nltk.tree.Tree:
        return []
    for child in root:
        if __is_eng_valid_np(child):
            nouns.append(' '.join(child.leaves()))
        else:
            extract_english_noun_phrases_aux(child, nouns)


def extract_english_noun_phrases(root) -> list[str]:
    str_root = str(root)
    if 'NP' not in str_root:
        return []

    nouns = []
    extract_english_noun_phrases_aux(root, nouns)
    return nouns


def __is_es_noun_exist(root):
    if type(root) != nltk.tree.Tree:
        return False
    if root.label() == 'NOUN':
        return True
    for child in root:
        if __is_es_noun_exist(child):
            return True
    return False


def __is_es_valid_np(root):
    if type(root) != nltk.tree.Tree:
        return False
    if root.label() != 'sn':
        return False
    return __is_es_noun_exist(root)


def extract_spanish_noun_phrases_aux(root, nouns):
    if type(root) != nltk.tree.Tree:
        return []
    for child in root:
        if __is_es_valid_np(child):
            nouns.append(' '.join(child.leaves()))
        else:
            extract_spanish_noun_phrases_aux(child, nouns)


def extract_spanish_noun_phrases(root) -> list[str]:
    str_root = str(root)
    if 'sn' not in  str_root:
        return []

    nouns = []
    extract_spanish_noun_phrases_aux(root, nouns)
    return nouns


def extract_noun_phrase(text, lang) -> list[str]:
    nlp = en_nlp if lang == 'eng' else es_nlp
    foo = extract_english_noun_phrases if lang == 'eng' else extract_spanish_noun_phrases

    doc = nlp(text)
    sentence = doc.sentences[0]
    root = nltk.tree.Tree.fromstring(str(sentence.constituency))
    if debug_print:
        root.pprint()
    return foo(root)


def read_games_data():
    df = pd.DataFrame(columns=['map', 'lang', 'speaker', 'text', 'nouns'])
    for file_name in tqdm(os.listdir(root_folder)):
        json_file = open(os.path.join(root_folder, file_name), encoding='utf8')
        data = json.load(json_file)

        version = data['server_version']
        experiment = experiments_short_names.get(version, 'err')
        if experiment not in experiments:
            continue

        for idx, game_data in enumerate(data['games_data']):
            map_idx = idx + 1
            role = game_data['config']['game_role']
            for uter in game_data['chat']:
                speaker = 'human' if uter['id'] == role else 'bot'
                if uter['lang'] == 'none':
                    continue
                elif uter['lang'] == 'mix':
                    continue

                text = uter['msg']
                lang = uter['lang']
                nouns = extract_noun_phrase(text, lang)
                if len(nouns):
                    row = {'map': map_idx, 'lang': lang, 'speaker': speaker, 'text': text, 'nouns': nouns}
                    df = pd.concat([df, pd.DataFrame(row)], ignore_index=True)

    df.to_csv('all_noun_phrase.csv')


if __name__ == '__main__':
    """
    run from root repo
    """
    en_nlp = stanza.Pipeline(lang='en', processors='tokenize,pos,constituency')
    es_nlp = stanza.Pipeline(lang='es', processors='tokenize,pos,constituency')

    # read_games_data()

    # debug
    debug_print = False
    en_text = [
        # "ok walk forward to the middle of the island and then pass the frog and circle back toward the rocks that are past the frog and then cross those to get to the next island",

        "circle back toward the rocks that are past the frog and then cross those to get to the next island",
        "the big black dog walked to the park",
        "cross over the snake and there is a small path that will lead you to the other island where the girraffe is"
    ]
    es_text = ['¿cuál es el siguiente paso después los amigos sapos?']
    for text in en_text:
        print(extract_noun_phrase(text, 'eng'))
    for text in es_text:
        print(extract_noun_phrase(text, 'es'))
