import pandas as pd
import json
import os
from collections import defaultdict
import datetime

root_folder = r"../data/tmp/"


def read_games_data():
    for file_name in os.listdir(root_folder):
        json_file = open(os.path.join(root_folder, file_name), encoding='utf8')
        data = json.load(json_file)
        print(data)
        data['clinet_version'] = '2.2.6_p'

        with open(f'data/tmp2/{file_name}', 'w') as f:
            json.dump(data, f)


if __name__ == '__main__':
    read_games_data()
