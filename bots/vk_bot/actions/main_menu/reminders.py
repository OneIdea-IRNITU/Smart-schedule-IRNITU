from vkbottle.bot import Message

from tools import keyboards, statistics
from functions import calculating_reminder_times, get_notifications_status


async def reminder_settings(ans: Message, storage, tz):
    chat_id = ans.from_id
    message = ans.text
    user = storage.get_vk_user(chat_id)

    if message == 'Напоминание 📣' and user.get('group'):
        time = user['notifications']
        # Проверяем стату напоминания
        if not time:
            time = 0
        await ans.answer(f'{get_notifications_status(time)}', keyboard=keyboards.make_inline_keyboard_notifications())

        statistics.add(action='Напоминание', storage=storage, tz=tz)

    elif message == 'Настройки ⚙' and user.get('group'):
        time = user['notifications']
        await ans.answer('Настройка напоминаний ⚙\n\n'
                         'Укажите за сколько минут до начала пары должно приходить сообщение',
                         keyboard=keyboards.make_inline_keyboard_set_notifications(time))
        statistics.add(action='Настройки', storage=storage, tz=tz)

    elif '-' == message:
        time = user['notifications']
        if time == 0:
            await ans.answer('Хочешь уйти в минус?', keyboard=keyboards.make_inline_keyboard_set_notifications(time))
            return
        time -= 5
        # Отнимаем и проверяем на положительность
        if time <= 0:
            time = 0
        storage.save_or_update_vk_user(chat_id=chat_id, notifications=time)
        await ans.answer('Минус 5 минут', keyboard=keyboards.make_inline_keyboard_set_notifications(time))
        return

    elif '+' == message:
        time = user['notifications']
        time += 5
        storage.save_or_update_vk_user(chat_id=chat_id, notifications=time)
        await ans.answer('Плюс 5 минут', keyboard=keyboards.make_inline_keyboard_set_notifications(time))

    elif message == 'Сохранить':

        # Сохраняем статус в базу
        time = user['notifications']

        group = storage.get_vk_user(chat_id=chat_id)['group']

        if storage.get_vk_user(chat_id=chat_id)['course'] == "None":
            schedule = storage.get_schedule_prep(group=group)['schedule']
        else:
            schedule = storage.get_schedule(group=group)['schedule']
        if time > 0:
            reminders = calculating_reminder_times(schedule=schedule, time=int(time))
        else:
            reminders = []
        storage.save_or_update_vk_user(chat_id=chat_id, notifications=time, reminders=reminders)

        await ans.answer(f'{get_notifications_status(time)}', keyboard=keyboards.make_keyboard_start_menu())
