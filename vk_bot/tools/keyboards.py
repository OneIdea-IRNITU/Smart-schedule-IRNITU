from vkbottle import Keyboard, KeyboardButtonColor, Text
import json
MAX_CALLBACK_RANGE = 41


def parametres_for_buttons_start_menu_vk(text, color):
    '''Возвращает параметры кнопок'''
    return {
        "action": {
            "type": "text",
            "payload": "{\"button\": \"" + "1" + "\"}",
            "label": f"{text}"
        },
        "color": f"{color}"
    }

def make_inline_keyboard_notifications():
    """ Кнопка 'Настройка уведомлений' """
    keyboard = Keyboard(one_time=False)
    keyboard.row()
    keyboard.add(Text(label='Настройки ⚙'), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Text(label='<==Назад'), color=KeyboardButtonColor.SECONDARY)
    return keyboard


def make_keyboard_start_menu():
    """ Клавиатура основного меню """
    keyboard = Keyboard(one_time=False)
    keyboard.row()
    keyboard.add(Text(label="Расписание 🗓"), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Text(label="Ближайшая пара ⏱"), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Text(label="Расписание на сегодня 🍏"), color=KeyboardButtonColor.SECONDARY)
    keyboard.row()
    keyboard.add(Text(label="Расписание на завтра 🍎"), color=KeyboardButtonColor.SECONDARY)
    keyboard.row()
    # keyboard.add(Text(label="Поиск 🔎"), color=KeyboardButtonColor.PRIMARY)
    # keyboard.add(Text(label="Другое ⚡"), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Text(label="Напоминание 📣"), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Text(label="Список команд"), color=KeyboardButtonColor.PRIMARY)
    return keyboard


def make_keyboard_commands():
    """ Клавиатура текстовых команд"""
    keyboard = Keyboard(one_time=False)
    keyboard.row()
    # keyboard.add(Text(label="about"), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Text(label="Авторы"), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Text(label="Регистрация"), color=KeyboardButtonColor.SECONDARY)
    keyboard.add(Text(label="Карта"), color=KeyboardButtonColor.SECONDARY)
    keyboard.row()
    keyboard.add(Text(label="<==Назад"), color=KeyboardButtonColor.SECONDARY)
    return keyboard


def make_keyboard_extra():
    """ Клавиатура дополнительных кнопок меню - Другое"""
    keyboard = Keyboard(one_time=False)
    keyboard.row()
    keyboard.add(Text(label="Список команд"), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Text(label="Напоминание 📣"), color=KeyboardButtonColor.SECONDARY)
    keyboard.row()
    keyboard.add(Text(label="<==Назад"), color=KeyboardButtonColor.SECONDARY)
    return keyboard


def make_keyboard_nearlesson():
    """ Клавиатура выбора недели """
    keyboard = Keyboard(one_time=False)
    keyboard.row()
    keyboard.add(Text(label="Текущая"), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Text(label="Следующая"), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Text(label="<==Назад"), color=KeyboardButtonColor.SECONDARY)
    return keyboard


def make_inline_keyboard_set_notifications(time=0):
    """ Клавиатура настройки уведомлений """

    if time != 0:
        text_check = f'{time} мин'
    else:
        text_check = 'off'

    keyboard = Keyboard(one_time=False)
    keyboard.row()
    keyboard.add(Text(label="-"), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Text(label=text_check), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Text(label='+'), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Text(label="Сохранить"), color=KeyboardButtonColor.SECONDARY)
    return keyboard


def make_keyboard_institutes(institutes=[]):
    """ Клавитура выбора института """

    keyboard = {
        "one_time": False
    }
    list_keyboard = []
    list_keyboard_main = []
    # list_keyboard.append(parametres_for_buttons_start_menu_vk('Преподаватель', 'primary'))
    # list_keyboard_main.append(list_keyboard)
    for institute in institutes:
        if len(institute['name']) >= MAX_CALLBACK_RANGE:
            name = sep_space(institute['name']) + ' ...'
        else:
            name = institute['name']
        list_keyboard = []
        list_keyboard.append(parametres_for_buttons_start_menu_vk(f'{name}', 'primary'))
        list_keyboard_main.append(list_keyboard)
    keyboard['buttons'] = list_keyboard_main
    keyboard = json.dumps(keyboard, ensure_ascii=False).encode('utf-8')
    keyboard = str(keyboard.decode('utf-8'))
    return keyboard


def make_keyboard_choose_course_vk(courses):
    """ Клавиатура для выбора курса """

    keyboard = {
        "one_time": False
    }
    list_keyboard_main = []
    for course in courses:
        name = course['name']
        list_keyboard = []
        list_keyboard.append(parametres_for_buttons_start_menu_vk(f'{name}', 'primary'))
        list_keyboard_main.append(list_keyboard)
    list_keyboard = []
    list_keyboard.append(parametres_for_buttons_start_menu_vk('Назад к институтам', 'primary'))
    list_keyboard_main.append(list_keyboard)
    keyboard['buttons'] = list_keyboard_main
    keyboard = json.dumps(keyboard, ensure_ascii=False).encode('utf-8')
    keyboard = str(keyboard.decode('utf-8'))
    return keyboard


def make_keyboard_choose_group_vk(groups=[]):
    """ Клавитура выбора группы """

    keyboard = {
        "one_time": False
    }
    list_keyboard_main_2 = []
    list_keyboard_main = []
    list_keyboard = []
    overflow = 0
    for group in groups:
        overflow += 1
        if overflow == 27:
            list_keyboard_main.append(list_keyboard)
            list_keyboard = []
            list_keyboard.append(parametres_for_buttons_start_menu_vk('Далее', 'primary'))
            list_keyboard.append(parametres_for_buttons_start_menu_vk('Назад к курсам', 'primary'))
            list_keyboard_main.append(list_keyboard)
        else:
            if overflow < 28:
                if len(list_keyboard) == 3:
                    list_keyboard_main.append(list_keyboard)
                    list_keyboard = []
                    list_keyboard.append(parametres_for_buttons_start_menu_vk(f'{group}', 'primary'))
                else:
                    list_keyboard.append(parametres_for_buttons_start_menu_vk(f'{group}', 'primary'))

            else:
                list_keyboard = []
                list_keyboard.append(parametres_for_buttons_start_menu_vk(f'{group}', 'primary'))
                list_keyboard_main_2.append(parametres_for_buttons_start_menu_vk(f'{group}', 'primary'))

    if overflow < 28:
        list_keyboard_main.append(list_keyboard)
        list_keyboard = []
        list_keyboard.append(parametres_for_buttons_start_menu_vk('Назад к курсам', 'primary'))
        list_keyboard_main.append(list_keyboard)
    else:
        list_keyboard_main_2.append(list_keyboard)

    keyboard['buttons'] = list_keyboard_main
    keyboard = json.dumps(keyboard, ensure_ascii=False).encode('utf-8')
    keyboard = str(keyboard.decode('utf-8'))

    return keyboard


def make_keyboard_choose_group_vk_page_2(groups=[]):
    """ Клавиатура для групп после переполнения первой """

    keyboard = {
        "one_time": False
    }
    groups = groups[26:]
    list_keyboard_main = []
    list_keyboard = []
    for group in groups:
        if len(list_keyboard) == 3:
            list_keyboard_main.append(list_keyboard)
            list_keyboard = []
            list_keyboard.append(parametres_for_buttons_start_menu_vk(f'{group}', 'primary'))
        else:
            list_keyboard.append(parametres_for_buttons_start_menu_vk(f'{group}', 'primary'))
    list_keyboard_main.append(list_keyboard)
    list_keyboard_main.append([parametres_for_buttons_start_menu_vk('Назад', 'primary')])

    keyboard['buttons'] = list_keyboard_main
    keyboard = json.dumps(keyboard, ensure_ascii=False).encode('utf-8')
    keyboard = str(keyboard.decode('utf-8'))
    return keyboard


def make_keyboard_choose_schedule():
    """ Клавиатура для выбора недели """

    keyboard = Keyboard(one_time=False)
    keyboard.row()
    keyboard.add(Text(label="На текущую неделю"), color=KeyboardButtonColor.PRIMARY)
    keyboard.add(Text(label="На следующую неделю"), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Text(label="Основное меню"), color=KeyboardButtonColor.SECONDARY)
    return keyboard


def make_keyboard_search_group(page, search_result=[]):
    """ Клавиатура поиска по группе """

    keyboard = {
        "one_time": False
    }

    list_keyboard_main_2 = []
    list_keyboard_main = []
    list_keyboard = []
    overflow = 0
    for group in search_result:
        group = group['search']
        overflow += 1
        if overflow == 25:
            list_keyboard_main.append(list_keyboard)
            list_keyboard = []
            if page == 1:
                list_keyboard.append(parametres_for_buttons_start_menu_vk('Основное меню', 'primary'))
                list_keyboard.append(parametres_for_buttons_start_menu_vk('Дальше', 'positive'))
                list_keyboard_main.append(list_keyboard)
            elif page > 1:
                list_keyboard.append(parametres_for_buttons_start_menu_vk('<==Назад', 'negative'))
                list_keyboard.append(parametres_for_buttons_start_menu_vk('Дальше', 'positive'))
                list_keyboard_main.append(list_keyboard)
                list_keyboard_main.append([parametres_for_buttons_start_menu_vk('Основное меню', 'primary')])

        else:
            if overflow < 26:
                if len(list_keyboard) == 3:
                    list_keyboard_main.append(list_keyboard)
                    list_keyboard = []
                    list_keyboard.append(parametres_for_buttons_start_menu_vk(f'{group}', 'primary'))
                else:
                    list_keyboard.append(parametres_for_buttons_start_menu_vk(f'{group}', 'primary'))

            else:
                list_keyboard = []
                list_keyboard.append(parametres_for_buttons_start_menu_vk(f'{group}', 'primary'))
                list_keyboard_main_2.append(parametres_for_buttons_start_menu_vk(f'{group}', 'primary'))

    if overflow < 26 and page > 1:
        list_keyboard_main.append(list_keyboard)
        list_keyboard = []
        list_keyboard.append(parametres_for_buttons_start_menu_vk('<==Назад', 'negative'))
        list_keyboard.append(parametres_for_buttons_start_menu_vk('Основное меню', 'primary'))
        list_keyboard_main.append(list_keyboard)

    elif overflow < 26:
        list_keyboard_main.append(list_keyboard)
        list_keyboard = []
        list_keyboard.append(parametres_for_buttons_start_menu_vk('Основное меню', 'primary'))
        list_keyboard_main.append(list_keyboard)
    else:
        list_keyboard_main_2.append(list_keyboard)

    keyboard['buttons'] = list_keyboard_main
    keyboard = json.dumps(keyboard, ensure_ascii=False).encode('utf-8')
    keyboard = str(keyboard.decode('utf-8'))

    return keyboard


def make_keyboard_main_menu():
    """ Клавиатура выхода в основное меню """

    keyboard = Keyboard(one_time=False)
    keyboard.row()
    keyboard.add(Text(label="Основное меню"), color=KeyboardButtonColor.PRIMARY)
    return keyboard

def make_keyboard_search():
    """ Клавиатура для поиска """

    keyboard = Keyboard(one_time=False)
    keyboard.row()
    keyboard.add(Text(label="Группы и преподаватели"), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Text(label="Аудитории"), color=KeyboardButtonColor.PRIMARY)
    keyboard.row()
    keyboard.add(Text(label="Основное меню"), color=KeyboardButtonColor.PRIMARY)
    return keyboard

def back_for_prep():
    """ Клавиатура перехода к старту регистрации для преподавателей """

    keyboard = Keyboard(one_time=False)
    keyboard.row()
    keyboard.add(Text(label="Назад к институтам"), color=KeyboardButtonColor.PRIMARY)
    return keyboard


def sep_space(name):
    """ Обрезает длину института, если тот больше 40 символов """

    dlina = abs(len(name) - MAX_CALLBACK_RANGE)
    name = name[:len(name) - dlina - 5]
    return name
