import math
import random
from time import sleep
from bots.rule_based.shared_utils import find_closest_object


class TemplateMatcherShare:
    def __init__(self, kb, chat):
        self.chat = chat
        self.kb_abs = kb['absolute']
        self.kb_path_order = list(self.kb_abs.keys())

        self.start_object = self.kb_path_order[0]
        self.goal_object = self.kb_path_order[-1]


        self.all_objects = []
        for key in self.kb_abs:
            self.all_objects.append({'obj': key, 'word': key})
            if 'synonym' in self.kb_abs[key]:
                self.all_objects.extend([{'obj': key, 'word': s} for s in self.kb_abs[key]['synonym']])

        self.where_to_suffix = ["where should i go?",
                                "where should i go now?",
                                "where do i need to go?",
                                "where do i have to go?",
                                "which direction should i take?",
                                "which direction should i go now?"
                                ]

        self.moved_prefix = ["ok, i did it, i'm next to the",
                             "awsome! as you said, i'm now near the",
                             'sure, i have reached the',
                             'awsome! i have reached the',
                         ]

        # State
        tmp = self.kb_abs[self.start_object]
        self.state = {'r': tmp['r'], 'c': tmp['c']}
        self.state_pth_idx = 0
        self.next_state_idx = 1
        self.next_state_obj = ''
        self.finish = False


    def update_state(self):
        if self.finish:
            return

        closest_obj = find_closest_object(self.state, self.kb_abs)
        self.state_pth_idx = self.kb_path_order.index(closest_obj)
        self.next_state_idx = self.state_pth_idx + 1
        if self.next_state_idx > len(self.kb_path_order) - 1:
            self.finish = True
            self.next_state_obj = self.goal_object
            return

        self.next_state_obj = self.kb_path_order[self.next_state_idx]

    def get_dist_to_next_state_obj(self) -> str:
        relative_col = ''
        if self.state['c'] > self.kb_abs[self.next_state_obj]['c']:
            relative_col = 'east'
        if self.state['c'] < self.kb_abs[self.next_state_obj]['c']:
            relative_col = 'west'

        relative_row = ''
        if self.state['r'] > self.kb_abs[self.next_state_obj]['r']:
            relative_row = 'south'
        if self.state['r'] < self.kb_abs[self.next_state_obj]['r']:
            relative_row = 'north'

        if relative_row and relative_col:
            relative_dir = f'{relative_row}-{relative_col}'
        elif relative_row:
            relative_dir = relative_row
        else:
            relative_dir = relative_col


        curr_coord = (self.state['r'], self.state['c'])
        next_coord = (self.kb_abs[self.next_state_obj]['r'], self.kb_abs[self.next_state_obj]['c'])
        steps = math.floor(math.dist(curr_coord, next_coord))

        if random.random() > 0.5:
            resp = f"i'm about {steps} steps {relative_dir} to the {self.next_state_obj}"
        else:
            resp = f"i'm {relative_dir} to the {self.next_state_obj}"

        return resp


    def advance_state_path_idx(self, adv):
        sleep(0.5)
        self.state_pth_idx += adv
        if self.state_pth_idx >= len(self.kb_path_order) - 1:
            self.finish = True
            self.state_pth_idx = len(self.kb_path_order) - 1

        obj_ = self.kb_path_order[self.state_pth_idx]
        tmp = self.kb_abs[obj_]
        self.state = {'r': tmp['r'], 'c': tmp['c']}

    def advance_state_path(self, axis, adv):
        """
        param: axis: row or col
        param: adv: amount to cells to advance
        """
        sleep(0.5)
        self.state[axis] += adv
        self.update_state()


    def obj_is_ahead(self):
        options = [
            "i have not reached the",
            "i didn't pass the",
            "i did not pass the",
            "i have not been at the",
            "i didn't walked through the"
        ]
        opt = random.choice(options)
        prefix = random.choice(["it's pretty far, ", 'but ', ''])
        return [f"{prefix}{opt} {self.next_state_obj} yet"]

    @staticmethod
    def obj_is_behind(obj_match):
        options = [
            "i have already passed by the",
            "i have already passed the",
            "i have already been at the",
            "i have already walked through the",
        ]
        opt = random.choice(options)
        return [f"{opt} {obj_match}"]
