import streamlit as st
import pandas as pd
import numpy as np
import json
import os
import altair as alt
from collections import defaultdict
import datetime
import math

from pages.common.versions import *
from pages.common.gt_path import *
from pages.common.dialog_analysis import *

default_rating_range = 'not at all: 0 -> extremely: 100'
rating_likely_range = 'not at all likely: 0 -> extremely likely: 100'
knowledge_range = 'no knowledge at all: 0 -> perfect, like a native speaker: 100'
time_range = 'never: 0 -> always: 100'
enjoy_range = 'not at all: 0 -> yes very much: 100'
natural_range = 'very unnatural :0 -> very natural: 100'

questions_ranges = {
    'How likely is your partner to be a fluent speaker of English?': rating_likely_range,
    'How likely do you think it was that you were talking to a chatbot rather than a human?': rating_likely_range,
    'How likely is your partner to be a fluent speaker of Spanish?': rating_likely_range,
    'How likely do you think it is that your partner is bilingual?': rating_likely_range,
    'Do you enjoy mixing languages in conversation?': enjoy_range,
    "How natural was your conversational partner’s language switching?": natural_range,
    'Age': ''
}

question_to_table = ['How much did you enjoy the task?',
                     "How successful do you think you were at completing the task?"]


def get_question_range_metadata(question: str):
    if question.startswith('Please rate how likely you are to use your'): return rating_likely_range
    if question.startswith('How would you rate your fluency in your '): return knowledge_range
    if question.startswith('When you switch languages'): return time_range
    return questions_ranges.get(question, default_rating_range)


def agg_dict_data_to_df(agg_data: dict):
    flat_exp = []
    flat_q = []
    flat_q_range = []
    flat_mean_ans = []
    flat_median_ans = []

    for exp in agg_data:
        for question in agg_data[exp]:
            answers = agg_data[exp][question]
            flat_exp.append(exp)
            flat_q.append(question)
            flat_q_range.append(get_question_range_metadata(question))
            flat_mean_ans.append(np.mean(answers))
            flat_median_ans.append(np.median(answers))

    return pd.DataFrame({
        "Experiment": flat_exp,
        "Question": flat_q,
        "Range": flat_q_range,
        "Mean": flat_mean_ans,
        "Median": flat_median_ans
    })


def mean_and_format_str(arr: list) -> str:
    return f"{np.mean(arr):.2f}"


def format_percentage(num: int) -> str:
    return f'{round(num * 100, 2)}%'


def avg_role_metadata(agg_metadata: defaultdict):
    samples = len(agg_metadata['game_time'])
    if samples == 0:
        return None

    res = {
        'number of games': samples,
        'mean game time': game_time_format(np.mean(agg_metadata['game_time'])),
        'median game time': game_time_format(np.median(agg_metadata['game_time']))
    }
    game_time_success_abs = np.count_nonzero(agg_metadata['is_time_success'])
    res['number of games finished before time is over'] = game_time_success_abs
    res['percentage of games finished before time is over'] = format_percentage(game_time_success_abs / samples)

    # dialog
    res['human - mean mean utterance length'] = mean_and_format_str(agg_metadata['user_mean_uter'])
    res['human - mean total number of tokens'] = mean_and_format_str(agg_metadata['user_total_uter'])
    res['human - mean number of utterances'] = mean_and_format_str(agg_metadata['user_num_of_uter'])
    human_mean_utters = np.mean(agg_metadata['user_num_of_uter'])
    human_mean_utters_en = np.mean(agg_metadata['user_num_of_en'])
    human_mean_utters_es = np.mean(agg_metadata['user_num_of_es'])
    human_mean_utters_mix = np.mean(agg_metadata['user_num_of_mix'])
    human_mean_utters_none = np.mean(agg_metadata['user_num_of_none'])
    human_mean_inter_cs = np.mean(agg_metadata['user_num_of_inter_cs'])

    res['human - mean number of eng utterances (%)'] = format_percentage(human_mean_utters_en / human_mean_utters)
    res['human - mean number of es utterances (%)'] = format_percentage(human_mean_utters_es / human_mean_utters)
    res['human - mean number of mixed utterances (%)'] = format_percentage(human_mean_utters_mix / human_mean_utters)
    res['human - mean number of none lng utterances (%)'] = format_percentage(
        human_mean_utters_none / human_mean_utters)

    # cong cs
    human_mean_num_uter_w_cong_cs = np.mean(agg_metadata['user_num_uter_with_ins_cs'])
    human_mean_num_of_total_cong_cs = np.mean(agg_metadata['user_num_of_total_ins_cs'])
    res['human - mean number of utterances with some ins switch (%)'] = format_percentage(
        human_mean_num_uter_w_cong_cs / human_mean_utters)
    res['human - mean number of total ins switches'] = mean_and_format_str(human_mean_num_of_total_cong_cs)
    res['human - mean number of cong masc switches (%)'] = format_percentage(
        np.mean(agg_metadata['user_num_of_cong_masc_cs']) / human_mean_num_of_total_cong_cs)
    res['human - mean number of cong fem switches (%)'] = format_percentage(
        np.mean(agg_metadata['user_num_of_cong_fem_cs']) / human_mean_num_of_total_cong_cs)
    res['human - mean number of incong masc (1) switches (%)'] = format_percentage(
        np.mean(agg_metadata['user_num_of_incong_masc_cs']) / human_mean_num_of_total_cong_cs)
    res['human - mean number of incong fem (2) switches (%)'] = format_percentage(
        np.mean(agg_metadata['user_num_of_incong_fem_cs']) / human_mean_num_of_total_cong_cs)
    res['human - mean number of NP switches (%)'] = format_percentage(
        np.mean(agg_metadata['user_num_of_np_cs']) / human_mean_num_of_total_cong_cs)
    res['human - mean number of ambiguous masc switches (%)'] = format_percentage(
        np.mean(agg_metadata['user_num_of_amb_masc_cs']) / human_mean_num_of_total_cong_cs)
    res['human - mean number of ambiguous fem switches (%)'] = format_percentage(
        np.mean(agg_metadata['user_num_of_amb_fem_cs']) / human_mean_num_of_total_cong_cs)

    human_total_det_cs = np.sum(agg_metadata['user_num_of_det_masc_cs'] + agg_metadata['user_num_of_det_fem_cs'])
    res['human - masc determiner cs (%) '] = format_percentage(
        np.sum(agg_metadata['user_num_of_det_masc_cs']) / human_total_det_cs)
    res['human - fem determiner cs (%) '] = format_percentage(
        np.sum(agg_metadata['user_num_of_det_fem_cs']) / human_total_det_cs)

    res['human - mean number of inter-sentential cs (%)'] = format_percentage(
        human_mean_inter_cs / (human_mean_utters - 1))
    res['human - mean % entrainment - all dialog'] = format_percentage(
        np.mean(agg_metadata['% entrainment - all dialog']))
    res['human - mean % entrainment - on bot inter-sentential cs'] = format_percentage(
        np.mean(agg_metadata['% entrainment - on bot inter-sentential cs']))

    res['bot - mean mean utterance length'] = mean_and_format_str(agg_metadata['bot_mean_uter'])
    res['bot - mean total number of tokens'] = mean_and_format_str(agg_metadata['bot_total_uter'])
    res['bot - mean number of utterances'] = mean_and_format_str(agg_metadata['bot_num_of_uter'])
    bot_mean_utters = np.mean(agg_metadata['bot_num_of_uter'])
    bot_mean_utters_en = np.mean(agg_metadata['bot_num_of_en'])
    bot_mean_utters_es = np.mean(agg_metadata['bot_num_of_es'])
    bot_mean_utters_mix = np.mean(agg_metadata['bot_num_of_mix'])
    bot_mean_utters_none = np.mean(agg_metadata['bot_num_of_none'])
    bot_mean_inter_cs = np.mean(agg_metadata['bot_num_of_inter_cs'])
    res['bot - mean number of eng utterances (%)'] = format_percentage(bot_mean_utters_en / bot_mean_utters)
    res['bot - mean number of es utterances (%)'] = format_percentage(bot_mean_utters_es / bot_mean_utters)
    res['bot - mean number of mixed utterances (%)'] = format_percentage(bot_mean_utters_mix / bot_mean_utters)
    res['bot - mean number of none lng utterances (%)'] = format_percentage(bot_mean_utters_none / bot_mean_utters)
    res['bot - mean number of inter-sentential cs (%)'] = format_percentage(bot_mean_inter_cs / (bot_mean_utters - 1))

    bot_mean_num_uter_w_cong_cs = np.mean(agg_metadata['bot_num_uter_with_ins_cs'])
    bot_mean_num_of_total_cong_cs = np.mean(agg_metadata['bot_num_of_total_ins_cs'])
    res['bot - mean number of utterances with some ins switch (%)'] = format_percentage(
        bot_mean_num_uter_w_cong_cs / bot_mean_utters)
    res['bot - mean number of total ins switches'] = mean_and_format_str(bot_mean_num_of_total_cong_cs)
    res['bot - mean number of cong masc switches (%)'] = format_percentage(
        np.mean(agg_metadata['bot_num_of_cong_masc_cs']) / bot_mean_num_of_total_cong_cs)
    res['bot - mean number of cong fem switches (%)'] = format_percentage(
        np.mean(agg_metadata['bot_num_of_cong_fem_cs']) / bot_mean_num_of_total_cong_cs)
    res['bot - mean number of incong masc (1) switches (%)'] = format_percentage(
        np.mean(agg_metadata['bot_num_of_incong_masc_cs']) / bot_mean_num_of_total_cong_cs)
    res['bot - mean number of incong fem (2) switches (%)'] = format_percentage(
        np.mean(agg_metadata['bot_num_of_incong_fem_cs']) / bot_mean_num_of_total_cong_cs)
    res['bot - mean number of NP switches (%)'] = format_percentage(
        np.mean(agg_metadata['bot_num_of_np_cs']) / bot_mean_num_of_total_cong_cs)
    res['bot - mean number of ambiguous masc switches (%)'] = format_percentage(
        np.mean(agg_metadata['bot_num_of_amb_masc_cs']) / bot_mean_num_of_total_cong_cs)
    res['bot - mean number of ambiguous fem switches (%)'] = format_percentage(
        np.mean(agg_metadata['bot_num_of_amb_fem_cs']) / bot_mean_num_of_total_cong_cs)

    bot_total_det_cs = np.sum(agg_metadata['bot_num_of_det_masc_cs'] + agg_metadata['bot_num_of_det_fem_cs'])
    res['bot - masc determiner cs (%) '] = format_percentage(
        np.sum(agg_metadata['bot_num_of_det_masc_cs']) / bot_total_det_cs)
    res['bot - fem determiner cs (%) '] = format_percentage(
        np.sum(agg_metadata['bot_num_of_det_fem_cs']) / bot_total_det_cs)

    for q in question_to_table:
        res[f"{q} [mean]"] = mean_and_format_str(agg_metadata[q])

    if 'dist_score' in agg_metadata:
        res['mean path distance'] = f"{np.mean(agg_metadata['dist_score']):.2f}"
    return res


def read_games_data() -> tuple[pd.DataFrame, dict, dict]:
    # first hierarchy is the experiment, 2nd is the survey
    agg_data = defaultdict(lambda: defaultdict(list))
    # first hierarchy is the experiment, 2nd is some metric we calculate
    agg_metadata_nav = defaultdict(lambda: defaultdict(list))
    agg_metadata_ins = defaultdict(lambda: defaultdict(list))

    for file_name in os.listdir(root_folder):
        json_file = open(os.path.join(root_folder, file_name), encoding='utf8')
        data = json.load(json_file)

        version = data['server_version']
        experiment = experiments_short_names.get(version, 'err')

        for game_data in data['games_data']:
            agg_meta = agg_metadata_ins

            if game_data['config']['game_role'] == 'navigator':
                # update to correct role
                agg_meta = agg_metadata_nav

                dist_score = path_dist(game_data['config']['map_index'], game_data['user_map_path'])
                agg_meta[experiment]['dist_score'].append(dist_score)

            game_time = game_data['game_time']
            agg_meta[experiment]['game_time'].append(game_time)
            max_game_time = time_success_metric(version=version)
            is_time_success = 1 if int(game_time) < max_game_time else 0
            agg_meta[experiment]['is_time_success'].append(is_time_success)

            user_dialog, bot_dialog = analysis_game_chat(game_data['config']['game_role'], game_data['chat'])
            if user_dialog is not None:
                agg_meta[experiment]['user_num_of_uter'].append(user_dialog['number of utterances'])
                agg_meta[experiment]['user_mean_uter'].append(user_dialog['mean utterance length'])
                agg_meta[experiment]['user_total_uter'].append(user_dialog['total number of tokens'])

                agg_meta[experiment]['user_num_of_en'].append(user_dialog['number of eng utterances'])
                agg_meta[experiment]['user_num_of_es'].append(user_dialog['number of es utterances'])
                agg_meta[experiment]['user_num_of_mix'].append(user_dialog['number of mix utterances'])
                agg_meta[experiment]['user_num_of_none'].append(user_dialog['number of none utterances'])
                agg_meta[experiment]['user_num_of_inter_cs'].append(user_dialog['number of inter-sentential cs'])

                agg_meta[experiment]['user_num_uter_with_ins_cs'].append(
                    user_dialog['number of utterances with some ins switch'])
                agg_meta[experiment]['user_num_of_total_ins_cs'].append(
                    user_dialog['number of total ins switches'])
                agg_meta[experiment]['user_num_of_cong_masc_cs'].append(user_dialog['number of cong_masc switches'])
                agg_meta[experiment]['user_num_of_cong_fem_cs'].append(user_dialog['number of cong_fem switches'])
                agg_meta[experiment]['user_num_of_np_cs'].append(user_dialog['number of NP switches'])
                agg_meta[experiment]['user_num_of_incong_masc_cs'].append(user_dialog['number of incong_masc switches'])
                agg_meta[experiment]['user_num_of_incong_fem_cs'].append(user_dialog['number of incong_fem switches'])
                agg_meta[experiment]['user_num_of_amb_masc_cs'].append(user_dialog['number of amb_masc switches'])
                agg_meta[experiment]['user_num_of_amb_fem_cs'].append(user_dialog['number of amb_fem switches'])

                agg_meta[experiment]['user_num_of_det_masc_cs'].append(user_dialog['number of masc det switches'])
                agg_meta[experiment]['user_num_of_det_fem_cs'].append(user_dialog['number of fem det switches'])

                agg_meta[experiment]['% entrainment - all dialog'].append(user_dialog['% entrainment - all dialog'])
                agg_meta[experiment]['% entrainment - on bot inter-sentential cs'].append(
                    user_dialog['% entrainment - on bot inter-sentential cs'])

            agg_meta[experiment]['bot_num_of_uter'].append(bot_dialog['number of utterances'])
            agg_meta[experiment]['bot_mean_uter'].append(bot_dialog['mean utterance length'])
            agg_meta[experiment]['bot_total_uter'].append(bot_dialog['total number of tokens'])

            agg_meta[experiment]['bot_num_of_en'].append(bot_dialog['number of eng utterances'])
            agg_meta[experiment]['bot_num_of_es'].append(bot_dialog['number of es utterances'])
            agg_meta[experiment]['bot_num_of_mix'].append(bot_dialog['number of mix utterances'])
            agg_meta[experiment]['bot_num_of_none'].append(bot_dialog['number of none utterances'])
            agg_meta[experiment]['bot_num_of_inter_cs'].append(bot_dialog['number of inter-sentential cs'])

            agg_meta[experiment]['bot_num_uter_with_ins_cs'].append(
                bot_dialog['number of utterances with some ins switch'])
            agg_meta[experiment]['bot_num_of_total_ins_cs'].append(bot_dialog['number of total ins switches'])
            agg_meta[experiment]['bot_num_of_cong_masc_cs'].append(bot_dialog['number of cong_masc switches'])
            agg_meta[experiment]['bot_num_of_cong_fem_cs'].append(bot_dialog['number of cong_fem switches'])
            agg_meta[experiment]['bot_num_of_np_cs'].append(bot_dialog['number of NP switches'])
            agg_meta[experiment]['bot_num_of_incong_masc_cs'].append(bot_dialog['number of incong_masc switches'])
            agg_meta[experiment]['bot_num_of_incong_fem_cs'].append(bot_dialog['number of incong_fem switches'])
            agg_meta[experiment]['bot_num_of_amb_masc_cs'].append(bot_dialog['number of amb_masc switches'])
            agg_meta[experiment]['bot_num_of_amb_fem_cs'].append(bot_dialog['number of amb_fem switches'])

            agg_meta[experiment]['bot_num_of_det_masc_cs'].append(bot_dialog['number of masc det switches'])
            agg_meta[experiment]['bot_num_of_det_fem_cs'].append(bot_dialog['number of fem det switches'])

            survey_data = data['map_survey'] if data['clinet_version'] >= '2.3.9_p' else game_data['survey']
            for qa in survey_data:
                question = qa['question']
                answer = qa['answer']
                agg_data[experiment][question].append(answer)

                if question in question_to_table:
                    agg_meta[experiment][question].append(answer)

    nav_more_data = defaultdict(lambda: defaultdict(dict))
    ins_more_data = defaultdict(lambda: defaultdict(dict))

    for exp in agg_data:
        nav_more_data[exp] = avg_role_metadata(agg_metadata_nav[exp])
        ins_more_data[exp] = avg_role_metadata(agg_metadata_ins[exp])

    df = agg_dict_data_to_df(agg_data)
    return df, nav_more_data, ins_more_data


def get_ex_date(data):
    game_data = data['games_data'][0]
    chat_ele = game_data['chat'][0]
    timestamp = chat_ele['timestamp']
    date_obj = datetime.datetime.fromtimestamp(timestamp / 1000.0)
    return date_obj.strftime("%D")


def get_human_role(data, experiment_version):
    if experiment_version >= '2.2.4_p':
        return 'Alternations'
    game_data = data['games_data'][0]
    return game_data['config']['game_role']


def game_time_format(t: int):
    mins = math.floor(t / 60)
    sec = math.floor(t % 60)
    sec = f'{sec}' if sec >= 10 else f'0{sec}'
    return f'{mins}:{sec}'


def read_general_data() -> tuple[pd.DataFrame, dict]:
    agg_data = defaultdict(lambda: defaultdict(list))
    count = defaultdict(int)
    more_data = defaultdict(lambda: defaultdict(dict))
    dates_data = defaultdict(lambda: set())

    for file_name in os.listdir(root_folder):
        json_file = open(os.path.join(root_folder, file_name), encoding='utf8')
        data = json.load(json_file)

        version = data['server_version']
        experiment = experiments_short_names.get(version, 'err')
        count[experiment] += 1
        dates_data[experiment].add(get_ex_date(data))
        more_data[experiment]['human_role'] = get_human_role(data, version)

        for qa in data['general_survey']:
            question = qa['question']
            answer = qa['answer']
            if type(answer) == int:
                agg_data[experiment][question].append(answer)
            elif question == 'Age:':
                agg_data[experiment]['Age'].append(int(answer))

    for ex in more_data:
        more_data[ex]['participants'] = count[ex]
        more_data[ex]['date'] = ', '.join(list(dates_data[ex]))

    df = agg_dict_data_to_df(agg_data)
    return df, more_data


def plot_chart(data, title, cols):
    selected_dfs = []
    for selected_ex in st.session_state.selected_ex:
        selected_dfs.append(data.loc[data['Experiment'] == selected_ex])
    if len(selected_dfs) == 0:
        return
    data = pd.concat(selected_dfs)

    sub_data = data[cols]
    chart = alt.Chart(sub_data, title=title).mark_bar().encode(
        x="Question:N",
        y=f"{title}:Q",
        xOffset="Experiment:N",
        color="Experiment:N",
        tooltip=cols

    )
    st.altair_chart(chart, use_container_width=True)


st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")
st.sidebar.success("Dashboard")

st.subheader("Experiments")

all_experiments = list(experiments_short_names.values())
# 'Baseline', 'Random CS', 'Short-context CS', 'Adversarial CS', 'Alignment CS'
selected_started_ex = ['Insertional Spanish Baseline', 'Insertional Spanish Congruent',
                       'Insertional Spanish Masculine InCongruent',
                       'Insertional Spanish Feminine InCongruent']

if 'selected_ex' not in st.session_state:
    st.session_state.selected_ex = selected_started_ex

st.session_state.selected_ex = st.multiselect('Choose experiment:', all_experiments, selected_started_ex)

games_data, navigator_ex_details, instructor_ex_details = read_games_data()
general_data, general_more_data = read_general_data()

general_ex_details = {}
navigator_det_copy = {}  # refresh on selected experiments
instructor_det_copy = {}
for key in experiments_short_names:
    name_key = experiments_short_names[key]
    if name_key not in st.session_state.selected_ex:
        continue
    if name_key not in general_more_data:
        continue
    general_ex_details[name_key] = {
        'details': version_details[key],
        'human role': general_more_data[name_key]['human_role'],
        'participants': general_more_data[name_key]['participants'],
        'date': general_more_data[name_key]['date']
    }
    navigator_det_copy[name_key] = navigator_ex_details[name_key]
    instructor_det_copy[name_key] = instructor_ex_details[name_key]

display_details_table = pd.DataFrame.from_dict(general_ex_details)
st.table(display_details_table)

st.subheader("Navigator")
nav_table = pd.DataFrame.from_dict(navigator_det_copy)
st.table(nav_table)
st.subheader("Instructor")
ins_table = pd.DataFrame.from_dict(instructor_det_copy)
st.table(ins_table)

st.subheader("Map Survey")
plot_chart(games_data, 'Mean', ['Question', 'Mean', 'Experiment', 'Range'])
plot_chart(games_data, 'Median', ['Question', 'Median', 'Experiment', 'Range'])

st.subheader("General Survey")
plot_chart(general_data, 'Mean', ['Question', 'Mean', 'Experiment', 'Range'])
plot_chart(general_data, 'Median', ['Question', 'Median', 'Experiment', 'Range'])
