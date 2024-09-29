import json
import os

from flask import Flask
from flask import request
from flask_cors import CORS

from bot_server import BotServer
from bots.cs_unit import CodeSwitchStrategyName
from google_cloud.storage import save_to_storage

VERSION = '2.4.1_p'

app = Flask(__name__)
CORS(app)

cs_strategy = CodeSwitchStrategyName.insertional_spanish_incongruent1
bot_server = BotServer(cs_strategy)

game_roles = {'navigator': 0, 'instructor': 1}
game_roles_reverse = {0: 'navigator', 1: 'instructor'}


@app.route('/api/v1/call_bot', methods=['POST'])
def call_bot():
    try:
        params = request.get_json()
        res, is_finish = bot_server.call_bot(params['guid'],
                                             params['msg'],
                                             params['map_index'],
                                             params['game_role'],
                                             params['state'])
        return json.dumps({'res': res, 'is_finish': is_finish}), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        print('err:', e)
        return "Server error", 500, {'Content-Type': 'application/json'}


@app.route('/api/v1/register', methods=['POST'])
def register():
    """
    client decide a role (nav/ins) and a map - we construct a bot that matches and return guid
    """
    try:
        params = request.get_json()
        guid, welcome_str = bot_server.register(params['map_index'], params['game_role'])
        resp = {'version': VERSION, 'guid': guid, 'welcome_str': welcome_str}
        return resp, 200, {'Content-Type': 'application/json'}
    except Exception as e:
        print('err:', e)
        return "Server error", 500, {'Content-Type': 'application/json'}


@app.route('/api/v1/upload', methods=['POST'])
def upload_api():
    try:
        params = request.get_json()

        upload_data = params
        upload_data['server_version'] = VERSION
        upload_data['cs_strategy'] = cs_strategy.value

        for game in upload_data['games_data']:
            cs_metadata = bot_server.get_cs_metadata(game['config']['guid'])
            game['cs_metadata'] = cs_metadata

            bot_server.un_register(game['config']['guid'])
            game['config']['game_role'] = game_roles_reverse[game['config']['game_role']]

            chat = game['chat']
            for c in chat:
                c['id'] = game_roles_reverse[c['id']]

        save_to_storage(upload_data, upload_data['prolific']['prolific_id'])
        return '', 200, {'Content-Type': 'application/json'}
    except Exception as e:
        print('err:', e)
        return "Server error", 500, {'Content-Type': 'application/json'}


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)
