from abc import ABCMeta, abstractmethod
from typing import List

from bots.models.lang_id_bert import LangIdBert
from google_cloud.translate import Translate


class CodeSwitchStrategy(metaclass=ABCMeta):
    def __init__(self):
        self.lid = LangIdBert()
        self.translate = Translate()

    @abstractmethod
    def call(self, user_msg: str, bot_resp: List[str]) -> tuple[list[str], bool]:
        """
        param user_msg: last user chat message
        param bot_resp: the generated messages (list) the bot generated
        :return: spanglish generated string in a list, bool if modified
        """
        pass

    def get_game_metadata(self):
        return []
