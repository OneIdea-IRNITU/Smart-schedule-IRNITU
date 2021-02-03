"""Запуск напоминаний от вк и tg в двух потоках"""
from threading import Thread

import telebot

from reminder import Reminder
from storage import MongodbService

import os

TG_TOKEN = os.environ.get('TOKEN')

storage = MongodbService().get_instance()

tg_bot = telebot.TeleBot(TG_TOKEN)
tg_reminder = Reminder(bot_platform='tg', bot=tg_bot, storage=storage)

vk_bot = None
# bot = Bot(f"{os.environ.get('VK')}")
# authorize = vk_api.VkApi(token=TOKEN)
vk_reminder = Reminder(bot_platform='vk', bot=vk_bot, storage=storage)

print(storage.get_schedule(group='ИБб-18-1')['schedule'][0]['lessons'])

def main():
    tg = Thread(target=tg_reminder.search_for_reminders)
    vk = Thread(target=vk_reminder.search_for_reminders)

    tg.start()
    vk.start()


if __name__ == '__main__':
    main()
