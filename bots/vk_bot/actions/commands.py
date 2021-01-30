from vkbottle.bot import Message
from tools import keyboards


async def start(ans: Message, chat_id: int, storage):
    """Команда бота Начать"""
    # Проверяем есть пользователь в базе данных
    if storage.get_vk_user(chat_id):
        storage.delete_vk_user_or_userdata(chat_id)  # Удаляем пользвателя из базы данных
    await ans.answer('Привет\n')
    await ans.answer('Для начала пройдите небольшую регистрацию😉\n')
    await ans.answer('Выберите институт.', keyboard=keyboards.make_keyboard_institutes(storage.get_institutes()))


async def registration(ans: Message, chat_id: int, storage):
    """Команда бота Регистрация"""
    # Проверяем есть пользователь в базе данных
    if storage.get_vk_user(chat_id):
        storage.delete_vk_user_or_userdata(chat_id)  # Удаляем пользвателя из базы данных
    await ans.answer('Повторная регистрация😉\n')
    await ans.answer('Выберите институт.', keyboard=keyboards.make_keyboard_institutes(storage.get_institutes()))


async def show_map(ans: Message, photo_vk_name: str):
    """Команда бота Карта"""
    await ans.answer('Карта университета', attachment=f'{photo_vk_name}',
                     keyboard=keyboards.make_keyboard_start_menu())


async def authors(ans: Message):
    """Команда бота Авторы"""
    await ans.answer('Авторы проекта:\n'
                     '-[id132677094|Алексей]\n'
                     '-[id128784852|Султан]\n'
                     '-[id169584462|Александр] \n'
                     '-[id135615548|Владислав]\n'
                     '-[id502898628|Кирилл]\n\n'
                     'По всем вопросом и предложениям пишите нам в личные сообщения. '
                     'Будем рады 😉\n', keyboard=keyboards.make_keyboard_start_menu()
                     )
