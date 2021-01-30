from vkbottle.bot import Message

from tools import keyboards, statistics


async def processing_main_buttons(ans: Message, storage, tz):
    chat_id = ans.from_id
    message = ans.text
    user = storage.get_vk_user(chat_id)

    if 'Основное меню' in message and user.get('group'):
        await ans.answer('Основное меню', keyboard=keyboards.make_keyboard_start_menu())
        statistics.add(action='Основное меню', storage=storage, tz=tz)

    elif '<==Назад' == message and user.get('group'):
        await ans.answer('Основное меню', keyboard=keyboards.make_keyboard_start_menu())

    elif 'Список команд' == message and user.get('group'):
        await ans.answer('Список команд:\n'
                         'Авторы - список авторов \n'
                         'Регистрация- повторная регистрация\n'
                         'Карта - карта университета', keyboard=keyboards.make_keyboard_commands())

        statistics.add(action='help', storage=storage, tz=tz)
        return

    elif 'Другое ⚡' == message and user.get('group'):
        await ans.answer('Другое', keyboard=keyboards.make_keyboard_extra())
        statistics.add(action='Другое', storage=storage, tz=tz)
        return

    elif 'Поиск 🔎' == message and user.get('group'):
        await ans.answer('Выберите, что будем искать', keyboard=keyboards.make_keyboard_search())
