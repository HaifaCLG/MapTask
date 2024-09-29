import spacy
import os
import json
from tqdm import tqdm

from app.pages.common.versions import experiments_short_names, root_folder
import pandas as pd

experiments = ['Baseline', 'Random CS', 'Short-context CS', 'Adversarial CS', 'Alignment CS']


def merge_phrases(doc):
    with doc.retokenize() as retokenizer:
        for np in list(doc.noun_chunks):
            attrs = {
                "tag": np.root.tag_,
                "lemma": np.root.lemma_,
                "ent_type": np.root.ent_type_,
            }
            retokenizer.merge(np, attrs=attrs)
    return doc


def extract_noun_phrase(text, lang) -> list[str]:
    nlp = en_nlp if lang == 'eng' else es_nlp
    doc = nlp(text)
    doc = merge_phrases(doc)

    nouns = []
    for token in doc:
        # print(token.text, token.pos_, token.dep_, token.head.text)
        if token.pos_ == 'NOUN':
            nouns.append(token.text)

    return nouns


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

    df.to_csv('all_noun_by_dep_phrase.csv')


if __name__ == '__main__':
    """
    run from root repo
    """

    en_nlp = spacy.load("en_core_web_sm")
    es_nlp = spacy.load("es_core_news_md")

    # read_games_data()

    # debug
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
