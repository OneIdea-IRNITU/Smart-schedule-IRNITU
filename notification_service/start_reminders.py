"""Запуск напоминаний от вк и tg в двух потоках"""
import os
from threading import Thread

import telebot
import vk_api

from reminder import Reminder
from storage import MongodbService

TG_TOKEN = os.environ.get('TG_TOKEN')
VK_TOKEN = os.environ.get('VK_TOKEN')

storage = MongodbService().get_instance()

tg_bot = telebot.TeleBot(TG_TOKEN)
tg_reminder = Reminder(bot_platform='tg', bot=tg_bot, storage=storage)


vk_bot = vk_api.VkApi(token=VK_TOKEN)
vk_reminder = Reminder(bot_platform='vk', bot=vk_bot, storage=storage)


def main():
    tg = Thread(target=tg_reminder.search_for_reminders)
    vk = Thread(target=vk_reminder.search_for_reminders)

    tg.start()
    vk.start()


if __name__ == '__main__':
    main()
