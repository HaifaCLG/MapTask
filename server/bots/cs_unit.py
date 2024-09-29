from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import List


class CodeSwitchStrategyName(str, Enum):
    none = "none"  # '2.3.1_p' alternation BASELINE
    alternation_random = "alternation_random"  # '2.3.2_p'
    alternation_short_context = "alternation_short_context_uter"  # '2.3.3_p'
    alternation_switch_last_user = "alternation_switch_last_user"  # '2.3.4_p'
    alternation_align_last_user = "alternation_align_last_user"  # '2.3.5_p'
    insertional_spanish_congruent = "insertional_spanish_congruent"  # '2.4.0_p'
    insertional_spanish_incongruent1 = "insertional_spanish_incongruent1"  # '2.4.1_p'
    insertional_spanish_incongruent2 = "insertional_spanish_incongruent2"  # '2.4.2_p'
    insertional_spanish_baseline = "insertional_spanish_baseline"  # '2.4.3_p"


class CSUnit(metaclass=ABCMeta):
    def __init__(self):
        pass

    @abstractmethod
    def call(self, user_msg: str, bot_resp: List[str]) -> List[str]:
        """
        param user_msg: last user chat message
        param bot_resp: the generated messages (list) the bot generated in (can be in either language)
        :return: spanglish generated string in a list
        """
        pass

    @abstractmethod
    def db_push(self) -> dict:
        """
        push state memory of the cs unit to DB
        return dict of state memory
        """
        pass

    @abstractmethod
    def db_load(self, data):
        """
        load / override state memory of the cs unit from DB
        """
        pass

    @abstractmethod
    def is_switched(self):
        """
        is last bot msg switched with some sort of CS strategy
        """
        pass

    @abstractmethod
    def get_game_metadata(self):
        pass
