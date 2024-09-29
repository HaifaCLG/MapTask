import re
import string
import math

question_words = {'what', 'when', 'where', 'why', 'which', 'who', 'whose', 'how', 'did', 'does', 'are', 'is'}
greeting_words = {'hi', 'hello', 'hey', 'hiya', 'howdy'}


def __tokenize(text):
    text = text.strip().lower()
    split = re.findall(fr'[${string.punctuation}]|\w+', text)
    return [t for t in split]


def is_question(text):
    tokens = __tokenize(text)
    if tokens[-1] == '?':
        return True
    return any(token in question_words for token in tokens)


def is_basic_greeting(text) -> bool:
    for token in __tokenize(text):
        if token in greeting_words:
            return True
    return False


def is_how_are_you_greeting(text) -> bool:
    t = text.lower()
    match = bool(re.match("(.*)(are you today)(.*)", t))
    match |= bool(re.match("(.*)(how are you)(.*)", t))
    match |= bool(re.match("(.*)(you doing)(.*)", t))
    match |= bool(re.match("(.*)(going on)(.*)", t))
    return match


def is_goal_match(text) -> bool:
    t = text.lower()
    match = bool(re.match("(.*)(what is (the|my) goal?)(.*)", t))
    match |= bool(re.match("(what (do|should) i do?)", t))
    match |= bool(re.match("(what am i expected to do?)", t))
    match |= bool(re.match("(what to do?)", t))
    return match


def find_closest_object(coord, kb_abs):
    """
    return the closest obj to the given coord - only objects from the abs KB!
    """
    curr_coord = (coord['r'], coord['c'])
    min_dist = 1000
    closest_obj = ''
    for obj in kb_abs:
        r = kb_abs[obj]['r']
        c = kb_abs[obj]['c']
        obj_coord = (r, c)
        curr_dist = math.dist(curr_coord, obj_coord)
        if curr_dist < min_dist:
            min_dist = curr_dist
            closest_obj = obj
    return closest_obj
