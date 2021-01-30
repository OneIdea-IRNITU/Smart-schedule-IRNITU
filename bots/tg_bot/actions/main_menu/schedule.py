from functions.creating_schedule import full_schedule_in_str, get_one_day_schedule_in_str, get_next_day_schedule_in_str
from functions.find_week import find_week
from functions.near_lesson import get_now_lesson
from tools import keyboards, statistics

from functions.logger import logger
from tools.check_schedule import check_schedule


def get_schedule(bot, message, storage, tz):
    chat_id = message.chat.id
    data = message.text

    user = storage.get_user(chat_id=chat_id)

    if 'Расписание 🗓' == data and user:
        try:
            bot.send_message(chat_id=chat_id, text='Выберите период',
                             reply_markup=keyboards.make_keyboard_choose_schedule())
        except Exception as e:
            logger.exception(e)
            return

        statistics.add(action='Расписание', storage=storage, tz=tz)

    elif ('На текущую неделю' == data or 'На следующую неделю' == data) and user:
        try:
            group = storage.get_user(chat_id=chat_id)['group']
        except Exception as e:
            logger.exception(e)
            return
        schedule = storage.get_schedule(group=group)

        # Проверяем есть ли у группы пользователя расписание
        if not check_schedule(bot=bot, chat_id=chat_id, schedule=schedule):
            return

        schedule = schedule['schedule']

        week = find_week()

        # меняем неделю
        if data == 'На следующую неделю':
            week = 'odd' if week == 'even' else 'even'

        week_name = 'четная' if week == 'odd' else 'нечетная'

        schedule_str = full_schedule_in_str(schedule, week=week)
        bot.send_message(chat_id=chat_id,
                         text=f'<b>Расписание {group}</b>\n'
                              f'Неделя: {week_name}', parse_mode='HTML',
                         reply_markup=keyboards.make_keyboard_start_menu())

        for schedule in schedule_str:
            bot.send_message(chat_id=chat_id,
                             text=f'{schedule}', parse_mode='HTML')

        statistics.add(action=data, storage=storage, tz=tz)

    elif 'Расписание на сегодня 🍏' in data and user:
        try:
            group = storage.get_user(chat_id=chat_id)['group']
        except Exception as e:
            logger.exception(e)
            return
        schedule = storage.get_schedule(group=group)

        # Проверяем есть ли у группы пользователя расписание
        if not check_schedule(bot=bot, chat_id=chat_id, schedule=schedule):
            return

        schedule = schedule['schedule']

        week = find_week()
        schedule_one_day = get_one_day_schedule_in_str(schedule=schedule, week=week)

        if not schedule_one_day:
            bot.send_message(chat_id=chat_id, text='Сегодня пар нет 😎')
            return

        bot.send_message(chat_id=chat_id,
                         text=f'{schedule_one_day}', parse_mode='HTML')

        statistics.add(action='Расписание на сегодня', storage=storage, tz=tz)

    elif 'Расписание на завтра 🍎' in data and user:
        try:
            group = storage.get_user(chat_id=chat_id)['group']
        except Exception as e:
            logger.exception(e)
            return
        schedule = storage.get_schedule(group=group)

        # Проверяем есть ли у группы пользователя расписание
        if not check_schedule(bot=bot, chat_id=chat_id, schedule=schedule):
            return

        schedule = schedule['schedule']

        week = find_week()
        schedule_next_day = get_next_day_schedule_in_str(schedule=schedule, week=week)

        if not schedule_next_day:
            bot.send_message(chat_id=chat_id, text='Завтра пар нет 😎')
            return

        bot.send_message(chat_id=chat_id,
                         text=f'{schedule_next_day}', parse_mode='HTML')

        statistics.add(action='Расписание на завтра', storage=storage, tz=tz)

    elif 'Ближайшая пара ⏱' in data and user:
        bot.send_message(chat_id, text='Ближайшая пара', reply_markup=keyboards.make_keyboard_nearlesson())

        statistics.add(action='Ближайшая пара', storage=storage, tz=tz)

    elif 'Текущая' in data and user:
        try:
            group = storage.get_user(chat_id=chat_id)['group']
        except Exception as e:
            logger.exception(e)
            return
        schedule = storage.get_schedule(group=group)

        # Проверяем есть ли у группы пользователя расписание
        if not check_schedule(bot=bot, chat_id=chat_id, schedule=schedule):
            return

        schedule = schedule['schedule']
        week = find_week()
        now_lessons = get_now_lesson(schedule=schedule, week=week)

        # если пар нет
        if not now_lessons:
            bot.send_message(chat_id=chat_id, text='Сейчас пары нет, можете отдохнуть')
            statistics.add(action='Текущая', storage=storage, tz=tz)
            return

        now_lessons_str = ''
        for near_lesson in now_lessons:
            name = near_lesson['name']
            if name == 'свободно':
                bot.send_message(chat_id=chat_id, text='Сейчас пары нет, можете отдохнуть',
                                 reply_markup=keyboards.make_keyboard_start_menu())
                return
            now_lessons_str += '-------------------------------------------\n'
            aud = near_lesson['aud']
            if aud:
                aud = f'Аудитория: {aud}\n'
            time = near_lesson['time']
            info = near_lesson['info'].replace(",", "")
            prep = near_lesson['prep']

            now_lessons_str += f'<b>{time}</b>\n' \
                               f'{aud}' \
                               f'👉{name}\n' \
                               f'{info} {prep}\n'
        now_lessons_str += '-------------------------------------------\n'
        bot.send_message(chat_id=chat_id, text=f'🧠Текущая пара🧠\n'
                                               f'{now_lessons_str}', parse_mode='HTML',
                         reply_markup=keyboards.make_keyboard_start_menu())

        statistics.add(action='Текущая', storage=storage, tz=tz)

    elif 'Следующая' in data and user:
        try:
            group = storage.get_user(chat_id=chat_id)['group']
        except Exception as e:
            logger.exception(e)
            return
        schedule = storage.get_schedule(group=group)

        # Проверяем есть ли у группы пользователя расписание
        if not check_schedule(bot=bot, chat_id=chat_id, schedule=schedule):
            return

        schedule = schedule['schedule']
        week = find_week()
        now_lessons = get_now_lesson(schedule=schedule, week=week)

        # если пар нет
        if not now_lessons:
            bot.send_message(chat_id=chat_id, text='Сегодня больше пар нет 😎',
                             reply_markup=keyboards.make_keyboard_start_menu())
            statistics.add(action='Следующая', storage=storage, tz=tz)
            return

        near_lessons_str = ''
        for near_lesson in now_lessons:
            name = near_lesson['name']
            if name == 'свободно':
                bot.send_message(chat_id=chat_id, text='Сегодня больше пар нет 😎',
                                 reply_markup=keyboards.make_keyboard_start_menu())
                return
            near_lessons_str += '-------------------------------------------\n'
            aud = near_lesson['aud']
            if aud:
                aud = f'Аудитория: {aud}\n'
            time = near_lesson['time']
            info = near_lesson['info'].replace(",", "")
            prep = near_lesson['prep']

            near_lessons_str += f'<b>{time}</b>\n' \
                                f'{aud}' \
                                f'👉{name}\n' \
                                f'{info} {prep}\n'
        near_lessons_str += '-------------------------------------------\n'
        bot.send_message(chat_id=chat_id, text=f'🧠Ближайшая пара🧠\n'
                                               f'{near_lessons_str}', parse_mode='HTML',
                         reply_markup=keyboards.make_keyboard_start_menu())

        statistics.add(action='Следующая', storage=storage, tz=tz)
