from datetime import datetime
from google.cloud import datastore
from singleton_decorator import singleton


@singleton
class Database:
    def __init__(self):
        self.client = datastore.Client(project='PROJECT NAME')
        self.kind = 'sync'

    def push(self, data, guid):
        key = self.client.key(self.kind, guid)
        ent = datastore.Entity(key)
        ent['time'] = datetime.now()
        ent.update(data)
        self.client.put(ent)

    def load(self, guid):
        key = self.client.key(self.kind, guid)
        ent = self.client.get(key)
        if ent is None:
            return None
        return ent
