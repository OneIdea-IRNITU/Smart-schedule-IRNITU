import os
from pymongo import MongoClient

MONGO_DB_ADDR = os.environ.get('MONGO_DB_ADDR')
MONGO_DB_PORT = os.environ.get('MONGO_DB_PORT')
MONGO_DB_DATABASE = os.environ.get('MONGO_DB_DATABASE')


class MongodbService(object):
    _instance = None
    _client = None
    _db = None

    @classmethod
    def get_instance(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls.__init__(cls._instance, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self._client = MongoClient(f'mongodb://{MONGO_DB_ADDR}:{MONGO_DB_PORT}')
        self._db = self._client[MONGO_DB_DATABASE]

    def get_data(self, collection) -> list:
        """возвращает список документов из указанной коллекции"""
        return list(self._db[collection].find())

    def save_data(self, collection, data: dict):
        """сохраняет документ в указанную коллекцию"""
        return self._db[collection].insert_one(data)

    def get_users_with_reminders_tg(self):
        return list(self._db.users.find(filter={'reminders': {'$ne': []}}))

    def get_users_with_reminders_vk(self):
        return list(self._db.VK_users.find(filter={'reminders': {'$ne': []}}))


    def get_schedule(self, group):
        """возвращает расписание группы"""
        return self._db.schedule.find_one(filter={'group': group})

    def save_status_tg(self, date, time):
        """сохраняем время последнего парса"""
        status = {
            'name': 'tg_reminders',
            'date': date,
            'time': time,
        }

        return self._db.status.update_one(filter={'name': 'tg_reminders'}, update={'$set': status}, upsert=True)

    def save_status_reminders_vk(self, date, time):
        """сохраняем время последнего парса"""
        status = {
            'name': 'vk_reminders',
            'date': date,
            'time': time,
        }

        return self._db.status.update_one(filter={'name': 'vk_reminders'}, update={'$set': status}, upsert=True)