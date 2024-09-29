from abc import abstractmethod, ABC
from typing import Union

from bots.rule_based.navigator.template_matchers.template_matcher_share import TemplateMatcherShare


class TemplateMatcher(ABC):
    def __init__(self, share: TemplateMatcherShare):
        self.shared = share

    @abstractmethod
    def match(self, user_msg) -> Union[list[str], None]:
        """
        param user_msg: last user chat message
        :return: generated template string in case of a match, else None
        """
