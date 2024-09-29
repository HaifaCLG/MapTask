import random
from abc import ABCMeta, abstractmethod
from typing import Tuple

from bots.cs_unit import CodeSwitchStrategyName

mixed_welcome_messages = [
    'hey, q tal? empezamos el juego?',
    'hey, estas listo?',
    'hey!!! ya comenzamos?',
    'hey there, estas listo?',
    'hola, you ready?',
    'hi there, empezamos?',
    'hola, q tal? ready to go?',
    'hola, q tal? ready to start?',
    'hola, q tal? ready to play?',
    'hi there! que comience el juego!!'
]

spanish_welcome_messages = [
    'hola, q tal? empezamos el juego?',
    'hola, estas listo?',
    'hola!!! ya comenzamos?',
    'hola, empezamos?',
    'hola! que comience el juego!!',
    'hola, q tal?'
]


class Bot(metaclass=ABCMeta):
    def __init__(self, cs_strategy: CodeSwitchStrategyName):
        self.messages = []
        self.is_spanish_cs_strategy = 'spanish' in cs_strategy

        welcome_msg_options = spanish_welcome_messages if self.is_spanish_cs_strategy else mixed_welcome_messages
        self.welcome_str = random.choice(welcome_msg_options)

    @abstractmethod
    def call(self, user_msg, user_state=None) -> Tuple[list[str], bool]:
        """
        param user_msg: last user chat message
        param user_state: current coordinate of user on the map (instructor bot only)
        :return: generated string in a list, flag if the bot has finished (navigator bot only)
        """

    @abstractmethod
    def db_push(self) -> dict:
        """
        push state memory of the bot to DB
        return dict of state memory
        """
        pass

    @abstractmethod
    def db_load(self, data):
        """
        load / override state memory of the bot from DB
        """
        pass

    def switch_and_override_memory(self, bot_switched_resp: list[str]):
        """
         in case the CS strategy overrides last msg. used by GPT bots.
         """
        for i in range(len(bot_switched_resp)):
            self.messages.pop()
        for new_msg in bot_switched_resp:
            self.messages.append({'role': 'assistant', 'content': new_msg})

    @staticmethod
    def informal_post_process(msg: str) -> list[str]:
        # return a list with up to 2 messages split by '.'
        messages = [m.strip() for m in msg.lower().split('.') if len(m)]
        if len(messages) > 2:
            mid = int(len(messages) / 2)
            return ['. '.join(messages[:mid]), '. '.join(messages[mid:])]

        return messages
