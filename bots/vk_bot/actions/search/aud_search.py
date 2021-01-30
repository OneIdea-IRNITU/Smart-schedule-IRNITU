from vkbottle.bot import Bot, Message

from functions import full_schedule_in_str_prep
from functions import find_week

from tools import keyboards, schedule_processing

aud_list = {}


async def start_search(bot: Bot, ans: Message, state):
    chat_id = ans.from_id
    aud_list[chat_id] = []
    await ans.answer('Введите интересующую аудитрию\n'
                     'Например: Ж-317, или Ж317', keyboard=keyboards.make_keyboard_main_menu())

    await bot.state_dispenser.set(ans.peer_id, state.AUD_SEARCH)


async def search(bot: Bot, ans: Message, storage):
    """Стейт поиска по аудиториям"""
    global aud_list
    # Чат ID пользователя
    chat_id = ans.from_id
    # Данные ввода
    data = ans.text
    # Соответствия по группам
    all_found_aud = []
    # Соответствия для преподов
    # Задаём состояние для первой страницы
    page = 1
    prep_list = []

    if not storage.get_schedule_aud(data) and len(ans.text.replace(' ', '')) < 15:
        # Отправляем запросы в базу посимвольно
        for item in data:
            # Получаем все результаты запроса на каждый символ
            request_item_all = storage.get_schedule_aud(item)
            # Проходим по каждому результату запроса одного символа
            for i in range(len(request_item_all)):
                # Обращаемся к результатам у которых есть ключ "aud"
                request_item = request_item_all[i]['aud']
                # Записывем все совпадения (Значения ключа "aud")
                prep_list.append(request_item)
                request_item = []

            request_item_all = []

        # Выделение наиболее повторяющихся элементов(а). Фактически результат запроса пользователя.
        qty_most_common = 0
        prep_list_set = set(prep_list)
        for item in prep_list_set:
            qty = prep_list.count(item)
            if qty > qty_most_common:
                qty_most_common = qty
                # Переменная с результатом сортировки
            if item.replace('-', '').lower() in ans.text.replace(' ', '').lower():
                data = item

    # Условие для первичного входа пользователя
    if storage.get_schedule_aud(data) and aud_list[chat_id] == []:
        # Результат запроса по аудам
        request_aud = storage.get_schedule_aud(data)
        # Циклы нужны для общего поиска. Здесь мы удаляем старые ключи в обоих реквестах и создаём один общий ключ, как для групп, так и для преподов
        for i in request_aud:
            i['search'] = i.pop('aud')
        # Записываем слово, которое ищем
        request_word = data
        # Отправляем в функцию данные для создания клавиатуры
        keyboard = keyboards.make_keyboard_search_group(page, request_aud)
        # Эти циклы записывают группы и преподов в нижнем регистре для удобной работы с ними
        for i in request_aud:
            all_found_aud.append(i['search'].lower())
        # Формируем полный багаж для пользователя
        list_search = [page, request_word, all_found_aud]
        # Записываем все данные под ключом пользователя
        aud_list[chat_id] = list_search
        # Выводим результат поиска с клавиатурой (кливиатур формируется по поисковому запросу)
        await ans.answer("Результат поиска", keyboard=keyboard)



    # Здесь уловия для выхода в основное меню
    elif data == "Основное меню":
        del aud_list[ans.from_id]
        await ans.answer("Основное меню", keyboard=keyboards.make_keyboard_start_menu())
        await bot.state_dispenser.delete(ans.peer_id)

    # Здесь уловие для слова "Дальше"
    elif data == "Дальше":
        page = aud_list[ans.from_id][0]
        aud_list[ans.from_id][0] += 1
        request_word = aud_list[ans.from_id][1]
        request_aud = storage.get_schedule_aud(request_word)
        for i in request_aud:
            i['search'] = i.pop('aud')
        request_aud = request_aud[26 * page:]
        keyboard = keyboards.make_keyboard_search_group(page + 1, request_aud)
        await ans.answer(f"Страница {page + 1}", keyboard=keyboard)

    # По аналогии со словом "<==Назад", только обратный процесс
    elif data == "<==Назад":
        aud_list[ans.from_id][0] -= 1
        page = aud_list[ans.from_id][0]
        request_word = aud_list[ans.from_id][1]
        request_aud = storage.get_schedule_aud(request_word)
        for i in request_aud:
            i['search'] = i.pop('aud')
        request_aud = request_aud[26 * (page - 1):]
        keyboard = keyboards.make_keyboard_search_group(page, request_aud)
        await ans.answer(f"Страница {page}", keyboard=keyboard)

    # Условие для вывода расписания для группы и преподавателя по неделям
    elif ('На текущую неделю' == data or 'На следующую неделю' == data):
        group = aud_list[ans.from_id][1]
        request_word = aud_list[ans.from_id][1]
        request_aud = storage.get_schedule_aud(request_word)
        # Если есть запрос для группы, то формируем расписание для группы, а если нет, то для препода
        schedule = request_aud[0]

        if schedule['schedule'] == []:
            await schedule_processing.sending_schedule_is_not_available(ans=ans)
            return

        schedule = schedule['schedule']
        week = find_week()

        # меняем неделю
        if data == 'На следующую неделю':
            week = 'odd' if week == 'even' else 'even'

        week_name = 'четная' if week == 'odd' else 'нечетная'

        aud = request_word

        schedule_str = full_schedule_in_str_prep(schedule, week=week, aud=aud)

        await ans.answer(f'Расписание {group}\n'
                         f'Неделя: {week_name}', keyboard=keyboards.make_keyboard_start_menu())

        # Отправка расписания
        await schedule_processing.sending_schedule(ans=ans, schedule_str=schedule_str)

        await bot.state_dispenser.delete(ans.peer_id)

    # Условия для завершения поиска, тобишь окончательный выбор пользователя
    elif storage.get_schedule_aud(data) and data.lower() in (i for i in aud_list[ans.from_id][2]):
        choose = data
        aud_list[ans.from_id][1] = choose
        request_word = aud_list[ans.from_id][1]
        request_aud = storage.get_schedule_aud(request_word)
        for i in request_aud:
            i['search'] = i.pop('aud')

        await ans.answer(f"Выберите неделю для аудитории {choose}", keyboard=keyboards.make_keyboard_choose_schedule())

        return
    # Общее исключения для разных случаем, которые могу сломать бота. (Практически копия первого IF)
    else:
        if aud_list[ans.from_id] and storage.get_schedule_aud(data):

            # Результат запроса по аудам
            request_aud = storage.get_schedule_aud(data)
            # Циклы нужны для общего поиска. Здесь мы удаляем старые ключи в обоих реквестах и создаём один общий ключ, как для групп, так и для преподов
            for i in request_aud:
                i['search'] = i.pop('aud')
            # Записываем слово, которое ищем
            request_word = data
            # Отправляем в функцию данные для создания клавиатуры
            keyboard = keyboards.make_keyboard_search_group(page, request_aud)
            # Эти циклы записывают группы и преподов в нижнем регистре для удобной работы с ними
            for i in request_aud:
                all_found_aud.append(i['search'].lower())
            # Формируем полный багаж для пользователя
            list_search = [page, request_word, all_found_aud]
            # Записываем все данные под ключом пользователя
            aud_list[chat_id] = list_search
            # Выводим результат поиска с клавиатурой (кливиатур формируется по поисковому запросу)
            await ans.answer("Результат поиска", keyboard=keyboard)

        else:
            # Проверяем есть ли результат на запрос с "-"
            if len(aud_list[chat_id]) == 3:
                aud_list[chat_id][1] = ''
                await ans.answer('Поиск не дал результатов 😕', keyboard=keyboards.make_keyboard_main_menu())
                return
            else:
                await ans.answer('Поиск не дал результатов 😕', keyboard=keyboards.make_keyboard_main_menu())
                return
