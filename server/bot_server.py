import uuid
from typing import Tuple

from bots.bot import Bot
from bots.cs_unit import CSUnit, CodeSwitchStrategyName
# from google_cloud.database import Database

from bots.gpt.gpt_bot_nav import GptBotNavigator
from bots.gpt.gpt_bot_ins import GptBotInstructor
from bots.gpt.code_switch_strategies.code_switch_strategies import CodeSwitchStrategies


class BotServer:
    """
    --- google DB is currently not used ---
    """
    def __init__(self, cs_strategy: CodeSwitchStrategyName):
        self.sessions = {}
        # self.database = Database()
        self.cs_strategy = cs_strategy

    def register(self, map_index, game_role, guid=None):
        if guid is None:
            guid = str(uuid.uuid4())
        map_id = f'map_{map_index + 1}'
        bot: Bot = GptBotNavigator(map_id, self.cs_strategy) if game_role == 1 else GptBotInstructor(map_id,
                                                                                                     self.cs_strategy)
        self.sessions[guid] = {
            'bot': bot,
            'cs': CodeSwitchStrategies(strategy=self.cs_strategy, welcome_str=bot.welcome_str)
        }
        return guid, bot.welcome_str

    def un_register(self, guid):
        if guid in self.sessions:
            del self.sessions[guid]

    def get_cs_metadata(self, guid):
        if not guid in self.sessions:
            return []
        cs_unit: CSUnit = self.sessions[guid]['cs']
        return cs_unit.get_game_metadata()

    def call_bot(self, guid, user_msg, map_idx, game_role, user_state=None) -> Tuple[list[str], bool]:
        db_data = None
        if guid not in self.sessions:
            print('guid not in self! getting DB')
            self.register(map_index=map_idx, game_role=game_role, guid=guid)
            # db_data = self.database.load(guid)

        bot: Bot = self.sessions[guid]['bot']
        cs_unit: CSUnit = self.sessions[guid]['cs']

        # if db_data is not None:
        #     print('db: ', db_data)
        #     cs_unit.db_load(db_data)
        #     bot.db_load(db_data)

        bot_resp, is_finish = bot.call(user_msg, user_state)
        spanglish_bot_resp = cs_unit.call(user_msg, bot_resp)
        if cs_unit.is_switched():
            bot.switch_and_override_memory(spanglish_bot_resp)

        # push to DB when call is finished
        # data = cs_unit.db_push()
        # data.update(bot.db_push())
        # self.database.push(data, guid)

        return spanglish_bot_resp, is_finish
