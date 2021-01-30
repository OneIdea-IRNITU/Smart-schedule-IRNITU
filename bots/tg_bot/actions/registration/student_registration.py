import json
from functions.logger import logger
from tools import keyboards


def start_student_reg(bot, message, storage):
    chat_id = message.message.chat.id
    message_id = message.message.message_id
    data = message.data

    # После того как пользователь выбрал институт
    if 'institute' in data:
        data = json.loads(data)
        courses = storage.get_courses(data['institute'])

        storage.save_or_update_tg_user(chat_id=chat_id,
                                       institute=data['institute'])  # Записываем в базу институт пользователя
        try:
            # Выводим сообщение со списком курсов
            bot.edit_message_text(message_id=message_id, chat_id=chat_id, text=f'Выберите курс',
                                  reply_markup=keyboards.make_inline_keyboard_choose_courses(courses))
        except Exception as e:
            logger.exception(e)
            return

    # После того как пользователь выбрал курс или нажал кнопку назад при выборе курса
    elif 'course' in data:
        data = json.loads(data)

        # Если нажали кнопку назад
        if data['course'] == 'back':
            storage.delete_tg_user_or_userdata(
                chat_id=chat_id)  # Удаляем информацию об институте пользователя из базы данных
            try:
                bot.edit_message_text(message_id=message_id, chat_id=chat_id,
                                      text='Выберите институт',
                                      reply_markup=keyboards.make_inline_keyboard_choose_institute(
                                          storage.get_institutes()))
                return
            except Exception as e:
                logger.exception(e)
                return

        storage.save_or_update_tg_user(chat_id=chat_id, course=data['course'])  # Записываем в базу курс пользователя
        user = storage.get_user(chat_id=chat_id)

        try:
            institute = user['institute']
            course = user['course']
            groups = storage.get_groups(institute=institute, course=course)
            # Выводим сообщение со списком групп
            bot.edit_message_text(message_id=message_id, chat_id=chat_id,
                                  text=f'Выберите группу',
                                  reply_markup=keyboards.make_inline_keyboard_choose_groups(groups))
        except Exception as e:
            logger.exception(e)
            return

    # После того как пользователь выбрал группу или нажал кнопку назад при выборе группы
    elif 'group' in data:
        data = json.loads(data)

        # Если нажали кнопку назад
        if data['group'] == 'back':
            # Удаляем информацию о курсе пользователя из базы данных
            storage.delete_tg_user_or_userdata(chat_id=chat_id,
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
                                      reply_markup=keyboards.make_inline_keyboard_choose_courses(courses))
                return
            except Exception as e:
                logger.exception(e)
                return

        storage.save_or_update_tg_user(chat_id=chat_id, group=data['group'])  # Записываем в базу группу пользователя

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
                         reply_markup=keyboards.make_keyboard_start_menu())
