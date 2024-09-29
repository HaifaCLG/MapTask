import queue
import time
import uuid
from collections import defaultdict
from apscheduler.schedulers.background import BackgroundScheduler


# package: APScheduler

class HumanServer:
    """"
    --UNUSED--
    """
    def __init__(self):
        self.sessions_roles = {}
        self.sessions_resp = {}
        self.listeners = defaultdict(list)

        self.role_timeout = 180
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(func=self.__clear_roles, trigger="interval", seconds=self.role_timeout + 10)
        self.scheduler.start()

    def __clear_roles(self):
        del_keys = []
        for k in self.sessions_roles:
            time_since = time.time() - self.sessions_roles[k]['time']
            print('time since: ', time_since)
            if time_since > self.role_timeout:
                del_keys.append(k)

        for dk in del_keys:
            print('clearing: ', dk)
            del_guid = self.sessions_roles[dk]['guid']
            del self.sessions_resp[del_guid]
            del self.sessions_roles[dk]
        print(self.sessions_roles)
        print(self.sessions_resp)

    @staticmethod
    def __format_sse(data: str):
        msg = f'data: {data}\n\n'
        return msg

    def listen(self, guid: str):
        q = queue.Queue(maxsize=2)
        self.listeners[guid].append(q)
        return q

    def announce(self, msg, guid: str):
        data = self.__format_sse(msg)
        for i in reversed(range(len(self.listeners[guid]))):
            try:
                self.listeners[guid][i].put_nowait(data)
            except queue.Full:
                del self.listeners[guid][i]

    def assign_role_api(self, map_index):
        if map_index not in self.sessions_roles:
            guid = str(uuid.uuid4())
            self.sessions_roles[map_index] = {'guid': guid, 'time': time.time()}
            self.sessions_resp[guid] = {}
            return 'navigator', guid
        else:
            guid = self.sessions_roles[map_index]['guid']
            del self.sessions_roles[map_index]
            return 'instructor', guid

    def upload(self, data):
        guid = data['guid']
        role = data['game_config']['game_role']
        self.sessions_resp[guid][role] = data
        if len(self.sessions_resp[guid]) == 1:
            return None
        else:
            combined_data = {}
            navigator_data = self.sessions_resp[guid][0]
            instructor_data = self.sessions_resp[guid][1]

            combined_data['guid'] = guid
            combined_data['game_config'] = {'game_mode': 'human'}

            combined_data['chat'] = navigator_data['chat']
            combined_data['navigator_metadata'] = navigator_data['user_metadata']
            combined_data['navigator_survey'] = navigator_data['user_survey']
            combined_data['user_map_path'] = navigator_data['user_map_path']

            # TODO: align to new schema
            combined_data['instructor_metadata'] = instructor_data['user_metadata']
            combined_data['instructor_survey'] = instructor_data['user_survey']

            combined_data['clinet_version'] = data['clinet_version']
            combined_data['map_metadata'] = data['map_metadata']

            del self.sessions_resp[guid]
            return combined_data
