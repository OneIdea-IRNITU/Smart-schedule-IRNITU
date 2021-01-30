from functions.calculating_reminder_times import calculating_reminder_times
from functions.notifications import get_notifications_status
from functions.logger import logger
from tools import keyboards, statistics
import json


def reminder_info(bot, message, storage, tz):
    chat_id = message.chat.id
    user = storage.get_user(chat_id=chat_id)

    if user:
        time = user['notifications']
        if not time:
            time = 0
        bot.send_message(chat_id=chat_id, text=get_notifications_status(time),
                         reply_markup=keyboards.make_inline_keyboard_notifications(time))

        statistics.add(action='Напоминания', storage=storage, tz=tz)


def reminder_settings(bot, message, storage, tz):
    chat_id = message.message.chat.id
    message_id = message.message.message_id
    data = message.data
    if 'notification_btn' in data:
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
                                  reply_markup=keyboards.make_inline_keyboard_set_notifications(time))
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
                                          reply_markup=keyboards.make_inline_keyboard_set_notifications(time))
        except Exception as e:
            logger.exception(e)
            return

    elif 'add_notifications' in data:
        data = json.loads(data)
        time = data['add_notifications']
        time += 5

        try:
            bot.edit_message_reply_markup(message_id=message_id, chat_id=chat_id,
                                          reply_markup=keyboards.make_inline_keyboard_set_notifications(time))
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
        storage.save_or_update_tg_user(chat_id=chat_id, notifications=time, reminders=reminders)

        try:
            bot.edit_message_text(message_id=message_id, chat_id=chat_id, text=get_notifications_status(time),
                                  reply_markup=keyboards.make_inline_keyboard_notifications(time))
        except Exception as e:
            logger.exception(e)
            return

        statistics.add(action='save_notifications', storage=storage, tz=tz)
