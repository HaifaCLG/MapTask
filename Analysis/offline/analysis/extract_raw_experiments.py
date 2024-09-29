"""
CSV format:
Each row in a single experiment-game
Each column is a "feature" e.g.: game_time, number of utterance
Extra columns: experiment name, human/bot and game role (navigator/instructor)
"""
from collections import defaultdict

import pandas as pd
import json
import os
from app.pages.common.dialog_analysis import analysis_game_chat
from app.pages.common.gt_path import path_dist
from app.pages.common.versions import experiments_short_names, root_folder, time_success_metric


def read_games_data():

    report_only = False

    df = pd.DataFrame()
    empty_nav_pids = defaultdict(lambda: set())

    for file_name in os.listdir(root_folder):
        json_file = open(os.path.join(root_folder, file_name), encoding='utf8')
        data = json.load(json_file)

        version = data['server_version']
        experiment = experiments_short_names.get(version, 'err')

        # check if nav is empty - ignore the whole participant
        if not report_only:
            nav_game_data = [data['games_data'][1], data['games_data'][3]]
            if any([len(gd['user_map_path']) == 1 for gd in nav_game_data]):
                continue

        for idx, game_data in enumerate(data['games_data']):
            game_role = game_data['config']['game_role']

            game_data_dict = {'experiment': experiment,
                              'human_role': game_role,
                              'map': idx,
                              'pid': file_name.split('.')[0]}

            if game_role == 'navigator':
                dist_score = path_dist(game_data['config']['map_index'], game_data['user_map_path'])
                game_data_dict['dist_score'] = dist_score
                if len(game_data['user_map_path']) == 1:
                    print(f'empty nav data: {experiment} - {file_name} - map: {idx}')
                    empty_nav_pids[experiment].add(file_name)

            game_time = game_data['game_time']
            max_game_time = time_success_metric(version=version)
            is_time_success = 1 if int(game_time) < max_game_time else 0
            game_data_dict['game_time'] = game_time
            game_data_dict['is_time_success'] = is_time_success

            user_dialog, bot_dialog = analysis_game_chat(game_data['config']['game_role'], game_data['chat'])
            if user_dialog is None:
                print(f'empty chat data: {experiment} - {file_name} - map: {idx}')
                continue

            for k in user_dialog:
                game_data_dict[f'user {k}'] = user_dialog[k]

            for k in bot_dialog:
                game_data_dict[f'bot {k}'] = bot_dialog[k]

            survey_data = data['map_survey'] if data['clinet_version'] >= '2.3.9_p' else game_data['survey']
            for qa in survey_data:
                game_data_dict[qa['question']] = qa['answer']

            for qa in data['general_survey']:
                game_data_dict[qa['question']] = qa['answer']

            df = pd.concat([df, pd.DataFrame.from_dict(game_data_dict, orient='index').T], ignore_index=True)

    if not report_only:
        df.to_csv(r'offline/analysis/raw_experiments.csv')
        print('saved')
    print(len(df))

    for e in empty_nav_pids:
        print(e, len(empty_nav_pids[e]))


if __name__ == '__main__':
    """
    run from root repo
    """
    read_games_data()
