from vkbottle.bot import Message

from actions import commands
from tools import keyboards, statistics


def name_institutes(institutes=[]):
    """ Храним список всех институтов """

    list_institutes = []
    for i in institutes:
        name = i['name']
        list_institutes.append(name)
    return list_institutes


def name_courses(courses=[]):
    """ Храним список всех курсов """

    list_courses = []
    for i in courses:
        name = i['name']
        list_courses.append(name)
    return list_courses


def name_groups(groups=[]):
    """ Храним список всех групп """

    list_groups = []
    for i in groups:
        name = i['name']
        list_groups.append(name)
    return list_groups


async def start_student_reg(ans: Message, storage, tz):
    chat_id = ans.from_id
    message_inst = ans.text
    message = ans.text
    user = storage.get_vk_user(chat_id)


    # Сохраняет в месседж полное название универ для корректного сравнения
    institutes = name_institutes(storage.get_institutes())
    for institute in institutes:
        if len(message_inst) > 5:
            if message_inst[:-5] in institute:
                message_inst = institute

    # Если пользователя нет в базе данных
    if not user:
        institutes = name_institutes(storage.get_institutes())
        # Смотрим выбрал ли пользователь институт
        if message_inst in institutes and ans.payload:
            # Если да, то записываем в бд
            storage.save_or_update_vk_user(chat_id=chat_id, institute=message_inst)
            await ans.answer(f'Вы выбрали: {message_inst}\n')
            await ans.answer('Выберите курс.',
                             keyboard=keyboards.make_keyboard_choose_course_vk(storage.get_courses(message_inst)))
        else:
            await commands.start(ans=ans, chat_id=chat_id, storage=storage)

    # Если нажал кнопку Назад к институтам
    elif message == "Назад к институтам" and not 'course' in user.keys():
        await ans.answer('Выберите институт.', keyboard=keyboards.make_keyboard_institutes(storage.get_institutes()))
        storage.delete_vk_user_or_userdata(chat_id=chat_id)
        return

    # Если нажал кнопку Назад к курсам
    elif message == "Назад к курсам" and not 'group' in user.keys():

        await ans.answer('Выберите курс.', keyboard=keyboards.make_keyboard_choose_course_vk(
            storage.get_courses(storage.get_vk_user(chat_id=chat_id)['institute'])))
        storage.delete_vk_user_or_userdata(chat_id=chat_id, delete_only_course=True)
        return

    # Регистрация после выбора института
    elif not 'course' in user.keys():
        institute = user['institute']
        course = storage.get_courses(institute)
        # Если нажал кнопку курса
        if message in name_courses(course):
            # Записываем в базу данных выбранный курс
            storage.save_or_update_vk_user(chat_id=chat_id, course=message)
            groups = storage.get_groups(institute=institute, course=message)
            groups = name_groups(groups)
            await ans.answer(f'Вы выбрали: {message}\n')
            await ans.answer('Выберите группу.', keyboard=keyboards.make_keyboard_choose_group_vk(groups))
            return
        else:
            await ans.answer('Не огорчай нас, мы же не просто так старались над клавиатурой 😼👇🏻',
                             keyboard=keyboards.make_keyboard_choose_course_vk(
                                 storage.get_courses(storage.get_vk_user(chat_id=chat_id)['institute']))
                             )
        return

    # Регистрация после выбора курса
    elif not 'group' in user.keys():
        institute = user['institute']
        course = user['course']
        groups = storage.get_groups(institute=institute, course=course)
        groups = name_groups(groups)
        # Если нажал кнопку группы
        if message in groups:
            # Записываем в базу данных выбранную группу
            storage.save_or_update_vk_user(chat_id=chat_id, group=message)
            await ans.answer('Вы успешно зарегистрировались!😊\n\n'
                             'Для того чтобы пройти регистрацию повторно, напишите сообщение "Регистрация"\n'
                             , keyboard=keyboards.make_keyboard_start_menu())
        else:
            if message == "Далее":
                await ans.answer('Выберите группу.', keyboard=keyboards.make_keyboard_choose_group_vk_page_2(groups))
            elif message == "Назад":
                await ans.answer('Выберите группу.', keyboard=keyboards.make_keyboard_choose_group_vk(groups))
            else:
                await ans.answer('Я очень сомневаюсь, что твоей группы нет в списке ниже 😉', keyboard=keyboards.make_keyboard_choose_group_vk(groups))
        return


    elif 'Далее' in message:
        await ans.answer('Далее', keyboard=keyboards.make_keyboard_choose_group_vk_page_2())

    elif user:
        await ans.answer('Такому ещё не научили 😇, знаю только эти команды:\n'
                         'Авторы - список авторов \n'
                         'Регистрация - повторная регистрация\n'
                         'Карта - карта университета', keyboard=keyboards.make_keyboard_start_menu())
    else:
        await ans.answer('Такому ещё не научили 😇, знаю только эти команды:\n'
                         'Авторы - список авторов \n'
                         'Регистрация - повторная регистрация\n'
                         'Карта - карта университета')
        statistics.add(action='bullshit', storage=storage, tz=tz)
