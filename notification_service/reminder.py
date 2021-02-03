import locale
import os
import platform
from datetime import datetime
from typing import Literal

import pytz

import tools
from logger import logger

VK_TOKEN = os.environ.get('VK')
TZ_IRKUTSK = pytz.timezone('Asia/Irkutsk')
locale_name = ('ru_RU.UTF-8' if platform.system() == 'Linux' else 'ru_RU')
locale.setlocale(locale.LC_TIME, locale_name)


# storage = MongodbService().get_instance()


class Reminder:

    def __init__(self, bot_platform: Literal['vk', 'tg'], bot, storage):
        self.platform = bot_platform
        self.__check_platform()
        self.bot = bot
        self.storage = storage
        self.users = []

    def sending_notifications(self):
        for user in self.users:
            chat_id = user['chat_id']
            week = user['week']
            day_now = user['day']
            time = user['time']
            group = user['group']
            notifications = user['notifications']

            schedule = self.storage.get_schedule(group=group)['schedule']

            # Получение расписания из нужного дня.
            lessons = tools.get_schedule_from_right_day(schedule=schedule, day_now=day_now)

            # если не нашлось переходем к след user
            if not lessons:
                continue

            lessons_for_reminders = tools.forming_message_text(lessons=lessons, week=week, time=time)

            # если пары не нашлись переходим к след user
            if not lessons_for_reminders:
                continue

            # Отправляем сообщение пользователю
            text = f'Через {notifications} минут пара\n' \
                   f'{lessons_for_reminders}'

            if self.platform == 'tg':
                try:
                    print(f'tg\n{text}')
                    self.bot.send_message(chat_id=chat_id, text=text)
                except Exception as e:
                    logger.exception(e)
            elif self.platform == 'vk':
                print(f'vk\n{text}')

    def __check_platform(self):
        """Проверка, что работает для такой платформы"""
        if self.platform == 'vk':
            logger.info('reminders_vk is started')
        elif self.platform == 'tg':
            logger.info('reminders_tg is started')
        else:
            raise ValueError(f'Нет такой платформы: {self.platform}')

    def search_for_reminders(self):

        minutes_old = None
        while True:
            # определяем время сейчас
            time_now = datetime.now(TZ_IRKUTSK)
            day_now = datetime.now(TZ_IRKUTSK).strftime('%A').lower()

            minutes_now = time_now.strftime('%M')

            if minutes_old != minutes_now:
                minutes_old = minutes_now  # нужно для того чтобы выполнить тело только один раз
                self.users = []

                # получаем пользователей у которых включены напоминания
                if self.platform == 'vk':
                    reminders = self.storage.get_users_with_reminders_vk()
                elif self.platform == 'tg':
                    reminders = self.storage.get_users_with_reminders_tg()

                for reminder in reminders:
                    week = tools.find_week()

                    if 'reminders' not in reminder.keys():
                        continue

                    # если у пользователя пустой reminders то None
                    user_days = reminder['reminders'].get(week)
                    if not user_days:
                        continue
                    # если у пользователя нет ткущего дня, то None
                    user_day_reminder_time = user_days.get(day_now.lower())

                    # если время совпадает с текущим, добавляем в список на отправку
                    if tools.check_that_user_has_reminder_enabled_for_the_current_time(time_now, user_day_reminder_time):
                        chat_id = reminder['chat_id']
                        group = reminder['group']
                        notifications = reminder['notifications']

                        user = tools.forming_user_to_submit(chat_id, group, notifications, day_now, time_now, week)
                        self.users.append(user)

                        logger.info(f'Добавили пользователя в список для отправки уведомлений: {reminder}')

                # после того как список сформирован, нужно отправить его боту
                self.sending_notifications()
