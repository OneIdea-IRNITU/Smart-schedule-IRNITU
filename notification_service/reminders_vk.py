import locale
import os
import platform
from datetime import datetime

import pytz
# import vk_api
from vkbottle.bot import Bot

import tools
from logger import logger
from storage import MongodbService

TOKEN = os.environ.get('VK')
TZ_IRKUTSK = pytz.timezone('Asia/Irkutsk')
locale_name = ('ru_RU.UTF-8' if platform.system() == 'Linux' else 'ru_RU')
locale.setlocale(locale.LC_TIME, locale_name)

bot = Bot(f"{os.environ.get('VK')}")

# authorize = vk_api.VkApi(token=TOKEN)

storage = MongodbService().get_instance()


def sending_notifications(users: list):
    for user in users:
        chat_id = user['chat_id']
        week = user['week']
        day_now = user['day']
        time = user['time']
        group = user['group']
        notifications = user['notifications']

        schedule = storage.get_schedule(group=group)['schedule']

        lessons = None
        for day in schedule:
            # находим нужный день
            if day['day'] == day_now:
                lessons = day['lessons']
                break
        # если не нашлось переходем к след user
        if not lessons:
            continue
        lessons_for_reminders = ''

        logger.info(f'Отправка сообщения пользователю. Notifications: {time}')
        logger.info(f'Занятия пользователя.  {lessons}')

        for lesson in lessons:
            lesson_time = lesson['time']
            # находим нужные пары (в нужное время)
            if time in lesson_time and (lesson['week'] == week or lesson['week'] == 'all'):
                name = lesson['name']
                # пропускаем свободные дни
                if name == 'свободно':
                    continue

                logger.info(f'Занятие на отправку: {lesson}')
                # формируем сообщение
                lessons_for_reminders += '--------------------------------------\n'
                aud = lesson['aud']
                if aud:
                    aud = f'Аудитория: {aud}\n'
                time = lesson['time']
                info = lesson['info']
                prep = lesson['prep']

                lessons_for_reminders += f'Начало в {time}\n' \
                                         f'{aud}' \
                                         f'{name}\n' \
                                         f'{info} {prep}\n'
                lessons_for_reminders += '--------------------------------------\n'
        # если пары не нашлись переходим к след user
        if not lessons_for_reminders:
            continue
        # отправляем сообщение пользователю
        text = f'Через {notifications} минут пара\n', f'{lessons_for_reminders}'

        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # ОТПРАВКА СООБЩЕНИЯ ПОЛЬЗОВАТЕЛЮ
        # authorize.method('messages.send', {'user_id': chat_id, 'message': text, 'random_id': 0})


def search_for_reminders():
    logger.info('reminders_vk is started')
    minutes_old = None
    while True:
        # определяем время сейчас
        time_now = datetime.now(TZ_IRKUTSK)
        day_now = datetime.now(TZ_IRKUTSK).strftime('%A').lower()

        minutes_now = time_now.strftime('%M')

        if minutes_old != minutes_now:
            minutes_old = minutes_now  # нужно для того чтобы выполнить тело только один раз
            users = []

            # получаем пользователей у которых включены напоминания
            reminders = storage.get_users_with_reminders_vk()

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
                if tools.check_the_reminder_time(time_now, user_day_reminder_time):
                    chat_id = reminder['chat_id']
                    group = reminder['group']
                    notifications = reminder['notifications']

                    user = tools.forming_user_to_submit(chat_id, group, notifications, day_now, time_now, week)
                    users.append(user)

                    logger.info(f'Добавили пользователя в список для отправки уведомлений: {reminder}')

            # после того как список сформирован, нужно отправить его боту
            sending_notifications(users)

            # записываем статистку
            date_now = datetime.now(TZ_IRKUTSK).strftime('%d.%m.%Y')
            time_now = datetime.now(TZ_IRKUTSK).strftime('%H:%M')
            storage.save_status_reminders_vk(date=date_now, time=time_now)


if __name__ == '__main__':
    search_for_reminders()
