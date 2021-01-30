from vkbottle.bot import Bot, Message

from functions.creating_schedule import full_schedule_in_str, full_schedule_in_str_prep
from functions.find_week import find_week
from functions.logger import logger
from tools import keyboards, schedule_processing

# Глобальная переменная(словарь), которая хранит в себе 3 состояния
# (номер страницы; слово, которые находим; список соответствия для выхода по условию в стейте)
Condition_request = {}


async def start_search(bot: Bot, ans: Message, state, storage):
    # ID пользователя
    chat_id = ans.from_id
    # Создаём ключ по значению ID пользователя
    Condition_request[chat_id] = []
    # Зарашиваем данные о пользователе из базы
    user = storage.get_vk_user(chat_id=chat_id)
    # Условие для проверки наличия пользователя в базе
    if user:
        # Запуск стейта со значением SEARCH
        await bot.state_dispenser.set(ans.peer_id, state.SEARCH)
        await ans.answer('Введите название группы или фамилию преподавателя\n'
                         'Например: ИБб-18-1 или Иванов', keyboard=keyboards.make_keyboard_main_menu())
    else:
        await ans.answer('Привет\n')
        await ans.answer('Для начала пройдите небольшую регистрацию😉\n')
        await ans.answer('Выберите институт.', keyboard=keyboards.make_keyboard_institutes(storage.get_institutes()))


async def search(bot: Bot, ans: Message, storage):
    """Стейт для работы поиска"""
    # Чат ID пользователя
    chat_id = ans.from_id
    # Данные ввода
    data = ans.text
    # Соответствия по группам
    all_found_groups = []
    # Соответствия для преподов
    all_found_prep = []
    # Задаём состояние для первой страницы
    page = 1
    # Логирование для информации в рил-тайм
    logger.info(f'Inline button data: {data}')
    # Условие для первичного входа пользователя
    if (storage.get_search_list(ans.text) or storage.get_search_list_prep(ans.text)) \
            and Condition_request[chat_id] == []:
        # Результат запроса по группам
        request_group = storage.get_search_list(ans.text)
        # Результат запроса по преподам
        request_prep = storage.get_search_list_prep(ans.text)
        # Циклы нужны для общего поиска. Здесь мы удаляем старые ключи в обоих реквестах и создаём один общий ключ, как для групп, так и для преподов
        for i in request_group:
            i['search'] = i.pop('name')
        for i in request_prep:
            i['search'] = i.pop('prep_short_name')
        # Записываем слово, которое ищем
        request_word = ans.text
        # Склеиваем результаты двух запросов для общего поиска
        request = request_group + request_prep
        # Отправляем в функцию данные для создания клавиатуры
        keyboard = keyboards.make_keyboard_search_group(page, request)
        # Эти циклы записывают группы и преподов в нижнем регистре для удобной работы с ними
        for i in request_group:
            all_found_groups.append(i['search'].lower())
        for i in request_prep:
            all_found_prep.append(i['search'].lower())
        # Создаём общий список
        all_found_results = all_found_groups + all_found_prep
        # Формируем полный багаж для пользователя
        list_search = [page, request_word, all_found_results]
        # Записываем все данные под ключом пользователя
        Condition_request[chat_id] = list_search
        # Выводим результат поиска с клавиатурой (кливиатур формируется по поисковому запросу)
        await ans.answer("Результат поиска", keyboard=keyboard)

    # Здесь уловия для выхода в основное меню
    elif ans.text == "Основное меню":
        del Condition_request[ans.from_id]
        await ans.answer("Основное меню", keyboard=keyboards.make_keyboard_start_menu())
        await bot.state_dispenser.delete(ans.peer_id)

    # Здесь уловие для слова "Дальше"
    elif ans.text == "Дальше":
        page = Condition_request[ans.from_id][0]
        Condition_request[ans.from_id][0] += 1
        request_word = Condition_request[ans.from_id][1]
        request_group = storage.get_search_list(request_word)
        request_prep = storage.get_search_list_prep(request_word)
        for i in request_group:
            i['search'] = i.pop('name')
        for i in request_prep:
            i['search'] = i.pop('prep_short_name')
        request = request_group + request_prep
        request = request[26 * page:]
        keyboard = keyboards.make_keyboard_search_group(page + 1, request)
        await ans.answer(f"Страница {page + 1}", keyboard=keyboard)

    # По аналогии со словом "<==Назад", только обратный процесс
    elif ans.text == "<==Назад":
        Condition_request[ans.from_id][0] -= 1
        page = Condition_request[ans.from_id][0]
        request_word = Condition_request[ans.from_id][1]
        request_group = storage.get_search_list(request_word)
        request_prep = storage.get_search_list_prep(request_word)
        for i in request_group:
            i['search'] = i.pop('name')
        for i in request_prep:
            i['search'] = i.pop('prep_short_name')
        request = request_group + request_prep
        request = request[26 * (page - 1):]
        keyboard = keyboards.make_keyboard_search_group(page, request)
        await ans.answer(f"Страница {page}", keyboard=keyboard)

    # Условие для вывода расписания для группы и преподавателя по неделям
    elif ('На текущую неделю' == data or 'На следующую неделю' == data):
        group = Condition_request[ans.from_id][1]
        request_word = Condition_request[ans.from_id][1]
        request_group = storage.get_search_list(request_word)
        request_prep = storage.get_search_list_prep(request_word)
        # Если есть запрос для группы, то формируем расписание для группы, а если нет, то для препода
        if request_group:
            schedule = storage.get_schedule(group=group)
        elif request_prep:
            schedule = request_prep[0]
        if schedule['schedule'] == []:
            await ans.answer('Расписание временно недоступно\nПопробуйте позже⏱')
            return

        schedule = schedule['schedule']
        week = find_week()

        # меняем неделю
        if data == 'На следующую неделю':
            week = 'odd' if week == 'even' else 'even'

        week_name = 'четная' if week == 'odd' else 'нечетная'
        if request_group:
            schedule_str = full_schedule_in_str(schedule, week=week)
        elif request_prep:
            schedule_str = full_schedule_in_str_prep(schedule, week=week)

        await ans.answer(f'Расписание {group}\n'
                         f'Неделя: {week_name}', keyboard=keyboards.make_keyboard_start_menu())
        # Отправка расписания
        await schedule_processing.sending_schedule(ans=ans, schedule_str=schedule_str)

        await bot.state_dispenser.delete(ans.peer_id)

    # Условия для завершения поиска, тобишь окончательный выбор пользователя
    elif (storage.get_search_list(ans.text) or storage.get_search_list_prep(ans.text)) and ans.text.lower() in \
            (i for i in Condition_request[ans.from_id][2]):
        choose = ans.text
        Condition_request[ans.from_id][1] = choose
        request_word = Condition_request[ans.from_id][1]
        request_group = storage.get_search_list(request_word)
        request_prep = storage.get_search_list_prep(request_word)
        for i in request_group:
            i['search'] = i.pop('name')
        for i in request_prep:
            i['search'] = i.pop('prep_short_name')
        if request_group:
            await ans.answer(f"Выберите неделю для группы {choose}", keyboard=keyboards.make_keyboard_choose_schedule())
        elif request_prep:
            await ans.answer(f"Выберите неделю для преподавателя {request_prep[0]['prep']}",
                             keyboard=keyboards.make_keyboard_choose_schedule())
        else:
            return
    # Общее исключения для разных случаем, которые могу сломать бота. (Практически копия первого IF)
    else:
        if Condition_request[ans.from_id] and storage.get_search_list(ans.text) or storage.get_search_list_prep(
                ans.text):
            request_group = storage.get_search_list(ans.text)
            request_prep = storage.get_search_list_prep(ans.text)
            for i in request_group:
                i['search'] = i.pop('name')
            for i in request_prep:
                i['search'] = i.pop('prep_short_name')
            request_word = ans.text
            request = request_group + request_prep
            keyboard = keyboards.make_keyboard_search_group(page, request)
            for i in request_group:
                all_found_groups.append(i['search'].lower())
            for i in request_prep:
                all_found_prep.append(i['search'].lower())
            all_found_results = all_found_groups + all_found_prep
            list_search = [page, request_word, all_found_results]
            Condition_request[chat_id] = list_search
            await ans.answer("Результат поиска", keyboard=keyboard)

        else:
            if len(Condition_request[chat_id]) == 3:
                Condition_request[chat_id][1] = ''
                await ans.answer('Поиск не дал результатов 😕')
                return
            else:
                await ans.answer('Поиск не дал результатов 😕')
                return
