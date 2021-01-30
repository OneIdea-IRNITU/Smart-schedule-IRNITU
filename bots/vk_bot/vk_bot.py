import os

import pytz
from vkbottle.bot import Bot, Message

from actions import commands
from actions.search import prep_and_group_search, aud_search
from actions.main_menu import reminders, main_menu, schedule
from actions.registration import teacher_registration, student_registration
from functions.storage import MongodbService
from tools.state import SuperStates
from tools import statistics

TOKEN = os.environ.get('VK')

storage = MongodbService().get_instance()
bot = Bot(TOKEN)  # TOKEN

content_schedule = {
    'text': ['Расписание 🗓', 'Ближайшая пара ⏱', 'Расписание на сегодня 🍏', 'На текущую неделю',
             'На следующую неделю',
             'Расписание на завтра 🍎', 'Следующая', 'Текущая']}

content_commands = {'text': ['Начать', 'начать', 'Начало', 'start']}

content_main_menu_buttons = {'text': ['Основное меню', '<==Назад', 'Список команд', 'Другое ⚡', 'Поиск 🔎']}

content_reminders = {'text': ['Напоминание 📣', 'Настройки ⚙', '-', '+', 'Сохранить']}

content_map = {'text': ['map', 'Карта', 'карта', 'Map', 'Схема', 'схема']}

TZ_IRKUTSK = pytz.timezone('Asia/Irkutsk')

map_image = "photo-198983266_457239216"


# ==================== ПОИСК ==================== #

@bot.on.message(text="Группы и преподаватели")
async def start_search_handler(ans: Message):
    """Вхождение в стейт поиска групп и преподавателей"""
    await prep_and_group_search.start_search(bot=bot, ans=ans, state=SuperStates, storage=storage)


@bot.on.message(state=SuperStates.SEARCH)
async def search_handler(ans: Message):
    """Стейт поиска групп и преподавателей"""
    await prep_and_group_search.search(bot=bot, ans=ans, storage=storage)


@bot.on.message(text="Аудитории")
async def start_aud_search_handler(ans: Message):
    """Вхождение в стейт поиска аудитории"""
    await aud_search.start_search(bot=bot, ans=ans, state=SuperStates)


@bot.on.message(state=SuperStates.AUD_SEARCH)
async def aud_search_handler(ans: Message):
    """Стейт поиска аудитории"""
    await aud_search.search(bot=bot, ans=ans, storage=storage)


# ==================== КОМАНДЫ ==================== #

@bot.on.message(text=content_commands['text'])
async def start_message_handler(ans: Message):
    """Команда Начать"""
    chat_id = ans.from_id
    await commands.start(ans=ans, chat_id=chat_id, storage=storage)
    statistics.add(action='start', storage=storage, tz=TZ_IRKUTSK)


@bot.on.message(text='Регистрация')
async def registration_handler(ans: Message):
    """Команда Регистрация"""
    chat_id = ans.from_id
    await commands.registration(ans=ans, chat_id=chat_id, storage=storage)
    statistics.add(action='reg', storage=storage, tz=TZ_IRKUTSK)


@bot.on.message(text=content_map['text'])
async def show_map_handler(ans: Message):
    """Команда Карта"""
    await commands.show_map(ans=ans, photo_vk_name=map_image)
    statistics.add(action='map', storage=storage, tz=TZ_IRKUTSK)


@bot.on.message(text='Авторы')
async def authors_handler(ans: Message):
    """Команда Авторы"""
    await commands.authors(ans=ans)
    statistics.add(action='authors', storage=storage, tz=TZ_IRKUTSK)


# ==================== РАСПИСАНИЕ ==================== #

@bot.on.message(text=content_schedule['text'])
async def schedule_handler(ans: Message):
    """Получение расписания"""
    await schedule.get_schedule(ans=ans, storage=storage, tz=TZ_IRKUTSK)


# ==================== ГЛАВНОЕ МЕНЮ ==================== #

@bot.on.message(text=content_main_menu_buttons['text'])
async def main_menu_buttons_handler(ans: Message):
    """Основные кнопки главног меню"""
    await main_menu.processing_main_buttons(ans=ans, storage=storage, tz=TZ_IRKUTSK)


# ==================== НАПОМИНАНИЯ ==================== #

@bot.on.message(text=content_reminders['text'])
async def reminders_handler(ans: Message):
    """Настройка напоминаний"""
    await reminders.reminder_settings(ans=ans, storage=storage, tz=TZ_IRKUTSK)


# ==================== РЕГИСТРАЦИЯ ==================== #

@bot.on.message(text="Преподаватель")
async def start_prep_reg_handler(ans: Message):
    """Вхождение в стейт регистрации преподавателей"""
    await teacher_registration.start_prep_reg(bot=bot, ans=ans, state=SuperStates, storage=storage)


@bot.on.message(state=SuperStates.PREP_REG)
async def reg_prep_handler(ans: Message):
    """Стейт регистрации преподавателей"""
    await teacher_registration.reg_prep(bot=bot, ans=ans, storage=storage)


@bot.on.message()  # Должно быть последним обработчиком, так как принимает все сообщения.
async def student_registration_handler(ans: Message):
    """Регистрация пользователя"""
    await student_registration.start_student_reg(ans=ans, storage=storage, tz=TZ_IRKUTSK)


def main():
    """Запуск бота"""
    bot.run_forever()


if __name__ == "__main__":
    main()
