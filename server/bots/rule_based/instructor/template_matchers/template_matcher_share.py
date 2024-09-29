import random

class TemplateMatcherShare:
    def __init__(self, kb, chat):
        self.chat = chat
        self.kb_abs = kb['absolute']
        self.kb_path_order = list(self.kb_abs.keys())
        self.start_object = self.kb_path_order[0]
        self.goal_object = self.kb_path_order[-1]
        self.outside_path = kb['outside_path']

        self.all_objects = []
        for key in self.kb_abs:
            self.all_objects.append({'obj': key, 'word': key})
            if 'synonym' in self.kb_abs[key]:
                self.all_objects.extend([{'obj': key, 'word': s} for s in self.kb_abs[key]['synonym']])

        for obj in self.outside_path:
            self.all_objects.append({'obj': obj, 'word': obj})


        self.closest_obj = None


    def get_kb_suggestion(self, object_) -> list[str]:
        curr_suggestion = random.choice(self.kb_abs[object_]['next_direction'])
        return [curr_suggestion] if type(curr_suggestion) == str else curr_suggestion
