import requests
import telebot

import pytz
from datetime import datetime
import os
from time import sleep

from functions.near_lesson import get_near_lesson, get_now_lesson
from functions.storage import MongodbService
from functions.logger import logger
from functions.creating_schedule import full_schedule_in_str, get_one_day_schedule_in_str, get_next_day_schedule_in_str
from functions.find_week import find_week
from functions.creating_buttons import *
from functions.calculating_reminder_times import calculating_reminder_times

from flask import Flask, request

TOKEN = os.environ.get('TOKEN')
HOST_URL = os.environ.get('HOST_URL')

TZ_IRKUTSK = pytz.timezone('Asia/Irkutsk')

bot = telebot.TeleBot(TOKEN, threaded=False)

storage = MongodbService().get_instance()

app = Flask(__name__)


# Обработка запросов от telegram
@app.route(f'/telegram-bot/{TOKEN}', methods=["POST"])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return 'ok', 200


# Проверка работы сервера бота
@app.route('/telegram-bot/status')
def status():
    return 'Бот активен', 200


# ==================== Обработка команд ==================== #

# Команда /start
@bot.message_handler(commands=['start'])
def start_message(message):
    chat_id = message.chat.id

    # Проверяем есть пользователь в базе данных
    if storage.get_user(chat_id):
        storage.delete_user_or_userdata(chat_id)  # Удаляем пользвателя из базы данных

    bot.send_message(chat_id=chat_id, text='Привет!\n')
    bot.send_message(chat_id=chat_id, text='Для начала пройдите небольшую регистрацию😉\n'
                                           'Выберите институт',
                     reply_markup=make_inline_keyboard_choose_institute(storage.get_institutes()))

    add_statistics(action='start')


# Команда /reg
@bot.message_handler(commands=['reg'])
def registration(message):
    chat_id = message.chat.id
    storage.delete_user_or_userdata(chat_id=chat_id)
    bot.send_message(chat_id=chat_id, text='Пройдите повторную регистрацию😉\n'
                                           'Выберите институт',
                     reply_markup=make_inline_keyboard_choose_institute(storage.get_institutes()))

    add_statistics(action='reg')


# Команда /help
@bot.message_handler(commands=['help'])
def help(message):
    chat_id = message.chat.id
    bot.send_message(chat_id=chat_id, text='Список команд:\n'
                                           '/about - описание чат бота\n'
                                           '/authors - Список авторов \n'
                                           '/reg - повторная регистрация \n'
                                           '/map - карта университета \n')

    add_statistics(action='help')


# Команда /map
@bot.message_handler(commands=['map'])
def map(message):
    chat_id = message.chat.id
    bot.send_photo(chat_id, (open('map.jpg', "rb")))
    # ФАЙЛОМ (РАБОТАЕТ)
    # map = open("map.jpg", "rb")
    # bot.send_document(chat_id, map)

    add_statistics(action='map')


# Команда /about
@bot.message_handler(commands=['about'])
def about(message):
    chat_id = message.chat.id
    bot.send_message(chat_id=chat_id, parse_mode='HTML',
                     text='<b>О боте:\n</b>'
                          'Smart schedule IRNITU bot - это чат бот для просмотра расписания занятий в '
                          'Иркутском национальном исследовательском техническом университете\n\n'
                          '<b>Благодаря боту можно:\n</b>'
                          '- Узнать актуальное расписание\n'
                          '- Нажатием одной кнопки увидеть информацию о ближайшей паре\n'
                          '- Настроить гибкие уведомления с информацией из расписания, '
                          'которые будут приходить за определённое время до начала занятия')

    add_statistics(action='about')


# Команда /authors
@bot.message_handler(commands=['authors'])
def authors(message):
    chat_id = message.chat.id
    bot.send_message(chat_id=chat_id, parse_mode='HTML',
                     text='<b>Авторы проекта:\n</b>'
                          '- Алексей @bolanebyla\n'
                          '- Султан @ace_sultan\n'
                          '- Александр @alexandrshen\n'
                          '- Владислав @TixoNNNAN\n'
                          '- Кирилл @ADAMYORT\n\n'
                          'По всем вопросом и предложениям пишите нам в личные сообщения. '
                          'Будем рады 😉\n'
                     )

    add_statistics(action='authors')


# ==================== Обработка Inline кнопок ==================== #
@bot.callback_query_handler(func=lambda call: True)
def handle_query(message):
    chat_id = message.message.chat.id
    message_id = message.message.message_id
    data = message.data

    logger.info(f'Inline button data: {data}')

    # После того как пользователь выбрал институт
    if 'institute' in data:
        data = json.loads(data)
        courses = storage.get_courses(data['institute'])

        institute = data['institute']

        storage.save_or_update_user(chat_id=chat_id,
                                    institute=data['institute'])  # Записываем в базу институт пользователя
        try:
            # Выводим сообщение со списком курсов
            bot.edit_message_text(message_id=message_id, chat_id=chat_id, text=f'Выберите курс',
                                  reply_markup=make_inline_keyboard_choose_courses(courses))
        except Exception as e:
            logger.exception(e)
            return

    # После того как пользователь выбрал курс или нажал кнопку назад при выборе курса
    elif 'course' in data:
        data = json.loads(data)

        # Если нажали кнопку назад
        if data['course'] == 'back':
            storage.delete_user_or_userdata(
                chat_id=chat_id)  # Удаляем информацию об институте пользователя из базы данных
            try:
                bot.edit_message_text(message_id=message_id, chat_id=chat_id,
                                      text='Выберите институт',
                                      reply_markup=make_inline_keyboard_choose_institute(storage.get_institutes()))
                return
            except Exception as e:
                logger.exception(e)
                return

        storage.save_or_update_user(chat_id=chat_id, course=data['course'])  # Записываем в базу курс пользователя
        user = storage.get_user(chat_id=chat_id)

        try:
            institute = user['institute']
            course = user['course']
            groups = storage.get_groups(institute=institute, course=course)
            # Выводим сообщение со списком групп
            bot.edit_message_text(message_id=message_id, chat_id=chat_id,
                                  text=f'Выберите группу',
                                  reply_markup=make_inline_keyboard_choose_groups(groups))
        except Exception as e:
            logger.exception(e)
            return

    # После того как пользователь выбрал группу или нажал кнопку назад при выборе группы
    elif 'group' in data:
        data = json.loads(data)

        # Если нажали кнопку назад
        if data['group'] == 'back':
            # Удаляем информацию о курсе пользователя из базы данных
            storage.delete_user_or_userdata(chat_id=chat_id,
                                            delete_only_course=True)
            try:
                institute = storage.get_user(chat_id=chat_id)['institute']
            except Exception as e:
                logger.exception(e)
                return
            courses = storage.get_courses(institute=institute)

            try:
                # Выводим сообщение со списком курсов
                bot.edit_message_text(message_id=message_id, chat_id=chat_id, text=f'Выберите курс',
                                      reply_markup=make_inline_keyboard_choose_courses(courses))
                return
            except Exception as e:
                logger.exception(e)
                return

        storage.save_or_update_user(chat_id=chat_id, group=data['group'])  # Записываем в базу группу пользователя

        try:
            # Удаляем меню регистрации
            bot.delete_message(message_id=message_id, chat_id=chat_id)
        except Exception as e:
            logger.exception(e)
            return

        bot.send_message(chat_id=chat_id,
                         text='Вы успешно зарегистрировались!😊\n\n'
                              'Для того чтобы пройти регистрацию повторно, воспользуйтесь командой /reg\n'
                              'Основные команды - /help',
                         reply_markup=make_keyboard_start_menu())

    elif 'notification_btn' in data:
        data = json.loads(data)
        if data['notification_btn'] == 'close':
            try:
                bot.delete_message(message_id=message_id, chat_id=chat_id)
                return
            except Exception as e:
                logger.exception(e)
                return
        time = data['notification_btn']

        try:
            bot.edit_message_text(message_id=message_id, chat_id=chat_id,
                                  text='Настройка напоминаний ⚙\n\n'
                                       'Укажите за сколько минут до начала пары должно приходить сообщение',
                                  reply_markup=make_inline_keyboard_set_notifications(time))
        except Exception as e:
            logger.exception(e)
            return

    elif 'del_notifications' in data:
        data = json.loads(data)
        time = data['del_notifications']
        if time == 0:
            return
        time -= 5

        if time < 0:
            time = 0

        try:
            bot.edit_message_reply_markup(message_id=message_id, chat_id=chat_id,
                                          reply_markup=make_inline_keyboard_set_notifications(time))
        except Exception as e:
            logger.exception(e)
            return

    elif 'add_notifications' in data:
        data = json.loads(data)
        time = data['add_notifications']
        time += 5

        try:
            bot.edit_message_reply_markup(message_id=message_id, chat_id=chat_id,
                                          reply_markup=make_inline_keyboard_set_notifications(time))
        except Exception as e:
            logger.exception(e)
            return

    elif 'save_notifications' in data:
        data = json.loads(data)
        time = data['save_notifications']

        group = storage.get_user(chat_id=chat_id)['group']

        schedule = storage.get_schedule(group=group)['schedule']
        if time > 0:
            reminders = calculating_reminder_times(schedule=schedule, time=int(time))
        else:
            reminders = []
        storage.save_or_update_user(chat_id=chat_id, notifications=time, reminders=reminders)

        try:
            bot.edit_message_text(message_id=message_id, chat_id=chat_id, text=get_notifications_status(time),
                                  reply_markup=make_inline_keyboard_notifications(time))
        except Exception as e:
            logger.exception(e)
            return

        add_statistics(action='save_notifications')


# =============================================================

def get_notifications_status(time):
    """Статус напоминаний"""
    if not time or time == 0:
        notifications_status = 'Напоминания выключены ❌\n' \
                               'Воспользуйтесь настройками, чтобы включить'
    else:
        notifications_status = f'Напоминания включены ✅\n' \
                               f'Сообщение придёт за {time} мин до начала пары 😇'
    return notifications_status


def get_text_schedule_not_available():
    text = 'Расписание временно недоступно🚫😣\n' \
           'Попробуйте позже⏱'
    return text


def check_schedule(chat_id, schedule) -> bool:
    """Проверяем есть ли у группы расписание"""
    if not schedule:
        bot.send_message(chat_id=chat_id,
                         text=get_text_schedule_not_available(),
                         reply_markup=make_keyboard_start_menu())
        return False
    if not schedule['schedule']:
        bot.send_message(chat_id=chat_id,
                         text=get_text_schedule_not_available(),
                         reply_markup=make_keyboard_start_menu())
        return False

    else:
        return True


def add_statistics(action: str):
    date_now = datetime.now(TZ_IRKUTSK).strftime('%d.%m.%Y')
    time_now = datetime.now(TZ_IRKUTSK).strftime('%H:%M')
    storage.save_statistics(action=action, date=date_now, time=time_now)


# =============================================================

# ==================== Обработка текста ==================== #
@bot.message_handler(content_types=['text'])
def text(message):
    chat_id = message.chat.id
    data = message.text

    logger.info(f'Message data: {data}')

    user = storage.get_user(chat_id=chat_id)

    if 'Расписание 🗓' == data and user:
        try:
            bot.send_message(chat_id=chat_id, text='Выберите период',
                             reply_markup=make_keyboard_choose_schedule())
        except Exception as e:
            logger.exception(e)
            return

        add_statistics(action='Расписание')

    elif ('На текущую неделю' == data or 'На следующую неделю' == data) and user:
        try:
            group = storage.get_user(chat_id=chat_id)['group']
        except Exception as e:
            logger.exception(e)
            return
        schedule = storage.get_schedule(group=group)

        # Проверяем есть ли у группы пользователя расписание
        if not check_schedule(chat_id=chat_id, schedule=schedule):
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
                         reply_markup=make_keyboard_start_menu())

        for schedule in schedule_str:
            bot.send_message(chat_id=chat_id,
                             text=f'{schedule}', parse_mode='HTML')

        add_statistics(action=data)

    elif 'Расписание на сегодня 🍏' in data and user:
        try:
            group = storage.get_user(chat_id=chat_id)['group']
        except Exception as e:
            logger.exception(e)
            return
        schedule = storage.get_schedule(group=group)

        # Проверяем есть ли у группы пользователя расписание
        if not check_schedule(chat_id=chat_id, schedule=schedule):
            return

        schedule = schedule['schedule']

        week = find_week()
        schedule_one_day = get_one_day_schedule_in_str(schedule=schedule, week=week)

        if not schedule_one_day:
            bot.send_message(chat_id=chat_id, text='Сегодня пар нет 😎')
            return

        bot.send_message(chat_id=chat_id,
                         text=f'{schedule_one_day}', parse_mode='HTML')

        add_statistics(action='Расписание на сегодня')

    elif 'Расписание на завтра 🍎' in data and user:
        try:
            group = storage.get_user(chat_id=chat_id)['group']
        except Exception as e:
            logger.exception(e)
            return
        schedule = storage.get_schedule(group=group)

        # Проверяем есть ли у группы пользователя расписание
        if not check_schedule(chat_id=chat_id, schedule=schedule):
            return

        schedule = schedule['schedule']

        week = find_week()
        schedule_next_day = get_next_day_schedule_in_str(schedule=schedule, week=week)

        if not schedule_next_day:
            bot.send_message(chat_id=chat_id, text='Завтра пар нет 😎')
            return

        bot.send_message(chat_id=chat_id,
                         text=f'{schedule_next_day}', parse_mode='HTML')

        add_statistics(action='Расписание на завтра')

    elif 'Ближайшая пара ⏱' in data and user:
        bot.send_message(chat_id, text='Ближайшая пара', reply_markup=make_keyboard_nearlesson())

        add_statistics(action='Ближайшая пара')

    elif 'Текущая' in data and user:
        try:
            group = storage.get_user(chat_id=chat_id)['group']
        except Exception as e:
            logger.exception(e)
            return
        schedule = storage.get_schedule(group=group)

        # Проверяем есть ли у группы пользователя расписание
        if not check_schedule(chat_id=chat_id, schedule=schedule):
            return

        schedule = schedule['schedule']
        week = find_week()
        now_lessons = get_now_lesson(schedule=schedule, week=week)

        # если пар нет
        if not now_lessons:
            bot.send_message(chat_id=chat_id, text='Сейчас пары нет, можете отдохнуть')
            add_statistics(action='Текущая')
            return

        now_lessons_str = ''
        for near_lesson in now_lessons:
            name = near_lesson['name']
            if name == 'свободно':
                bot.send_message(chat_id=chat_id, text='Сейчас пары нет, можете отдохнуть',
                                 reply_markup=make_keyboard_start_menu())
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
                         reply_markup=make_keyboard_start_menu())

        add_statistics(action='Текущая')

    elif 'Следующая' in data and user:
        try:
            group = storage.get_user(chat_id=chat_id)['group']
        except Exception as e:
            logger.exception(e)
            return
        schedule = storage.get_schedule(group=group)

        # Проверяем есть ли у группы пользователя расписание
        if not check_schedule(chat_id=chat_id, schedule=schedule):
            return

        schedule = schedule['schedule']
        week = find_week()
        now_lessons = get_now_lesson(schedule=schedule, week=week)

        # если пар нет
        if not now_lessons:
            bot.send_message(chat_id=chat_id, text='Сегодня больше пар нет 😎', reply_markup=make_keyboard_start_menu())
            add_statistics(action='Следующая')
            return

        near_lessons_str = ''
        for near_lesson in now_lessons:
            name = near_lesson['name']
            if name == 'свободно':
                bot.send_message(chat_id=chat_id, text='Сегодня больше пар нет 😎',
                                 reply_markup=make_keyboard_start_menu())
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
                         reply_markup=make_keyboard_start_menu())

        add_statistics(action='Следующая')

    elif 'Напоминание 📣' in data and user:
        time = user['notifications']
        if not time:
            time = 0
        bot.send_message(chat_id=chat_id, text=get_notifications_status(time),
                         reply_markup=make_inline_keyboard_notifications(time))

        add_statistics(action='Напоминания')

    elif 'Основное меню' in data and user:
        bot.send_message(chat_id, text='Основное меню', reply_markup=make_keyboard_start_menu())

        add_statistics(action='Основное меню')

    elif 'Авторы' == data and user:
        bot.send_message(chat_id, parse_mode='HTML', text='<b>Авторы проекта:\n</b>'
                                                          '- Алексей @bolanebyla\n'
                                                          '- Султан @ace_sultan\n'
                                                          '- Александр @alexandrshen\n'
                                                          '- Владислав @TixoNNNAN\n'
                                                          '- Кирилл @ADAMYORT\n\n'
                                                          'По всем вопросом и предложениям пишите нам в личные сообщения. '
                                                          'Будем рады 😉\n')

        add_statistics(action='Авторы')

    elif 'Список команд' in data and user:
        bot.send_message(chat_id, text='Список команд:\n'
                                       'Авторы - список авторов \n'
                                       'Регистрация- повторная регистрация\n'
                                       'Карта - карта университета', reply_markup=make_keyboard_commands())

        add_statistics(action='Другое')

    elif 'Другое ⚡' in data and user:
        bot.send_message(chat_id, text='Другое', reply_markup=make_keyboard_extra())

        add_statistics(action='Другое')

    elif 'Регистрация' in data and user:
        bot.send_message(chat_id=chat_id, text='Пройдите повторную регистрацию😉\n'
                                               'Выберите институт',
                         reply_markup=make_inline_keyboard_choose_institute(storage.get_institutes()))

    elif 'Карта' in data and user:
        bot.send_message(chat_id=chat_id, text='Подождите, карта загружается...')
        bot.send_photo(chat_id, (open('map.jpg', "rb")))
        add_statistics(action='Карта')

    else:
        if user:
            bot.send_message(chat_id, text='Я вас не понимаю 😞', reply_markup=make_keyboard_start_menu())
        else:
            bot.send_message(chat_id, text='Я вас не понимаю 😞')

        add_statistics(action='bullshit')


if __name__ == '__main__':
    bot.remove_webhook()
    logger.info('Бот запущен локально')
    bot.infinity_polling()
else:
    bot.remove_webhook()
    sleep(1)
    bot.set_webhook(url=f'{HOST_URL}/telegram-bot/{TOKEN}')
