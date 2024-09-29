import random

option_resp = ['where are you now?',
               'what do you see in front of you now?',
               "now, what is in front of you?"]


def engage_next() -> str:
    return random.choice(option_resp)
