from datetime import datetime

from vkbottle.bot import Message

from API.functions_api import find_week, full_schedule_in_str, full_schedule_in_str_prep, \
    get_one_day_schedule_in_str_prep, get_one_day_schedule_in_str, get_next_day_schedule_in_str, \
    get_next_day_schedule_in_str_prep, APIError, get_now_lesson_in_str_stud, get_now_lesson_in_str_prep
from API.functions_api import get_near_lesson, get_now_lesson
from tools import keyboards, statistics, schedule_processing


async def get_schedule(ans: Message, storage, tz):
    chat_id = ans.from_id
    data = ans.text
    user = storage.get_vk_user(chat_id=chat_id)

    if 'Расписание 🗓' == data and user.get('group'):
        await ans.answer('Выберите период\n', keyboard=keyboards.make_keyboard_choose_schedule())
        statistics.add(action='Расписание', storage=storage, tz=tz)

    if ('На текущую неделю' == data or 'На следующую неделю' == data) and user.get('group'):
        # Если курс нуль, тогда это преподаватель
        if storage.get_vk_user(chat_id=chat_id)['course'] != 'None':
            group = storage.get_vk_user(chat_id=chat_id)['group']
            schedule = storage.get_schedule(group=group)
        elif storage.get_vk_user(chat_id=chat_id)['course'] == 'None':
            group = storage.get_vk_user(chat_id=chat_id)['group']
            schedule = storage.get_schedule_prep(group=group)
        if not schedule or schedule['schedule'] == []:
            await ans.answer('Расписание временно недоступно\nПопробуйте позже⏱')
            statistics.add(action=data, storage=storage, tz=tz)
            return

        schedule = schedule['schedule']
        week = find_week()

        # меняем неделю
        if data == 'На следующую неделю':
            week = 'odd' if week == 'even' else 'even'

        week_name = 'четная' if week == 'odd' else 'нечетная'

        if storage.get_vk_user(chat_id=chat_id)['course'] != 'None':
            schedule_str = full_schedule_in_str(schedule, week=week)
        elif storage.get_vk_user(chat_id=chat_id)['course'] == 'None':
            schedule_str = full_schedule_in_str_prep(schedule, week=week)

        # Проверяем, что расписание сформировалось
        if isinstance(schedule_str, APIError):
            await schedule_processing.sending_schedule_is_not_available(ans=ans)
            return

        await ans.answer(f'Расписание {group}\n'
                         f'Неделя: {week_name}', keyboard=keyboards.make_keyboard_start_menu())

        # Отправка расписания
        await schedule_processing.sending_schedule(ans=ans, schedule_str=schedule_str)

        statistics.add(action=data, storage=storage, tz=tz)



    elif 'Расписание на сегодня 🍏' == data and user.get('group'):
        # Если курс нуль, тогда это преподаватель
        if storage.get_vk_user(chat_id=chat_id)['course'] != 'None':
            group = storage.get_vk_user(chat_id=chat_id)['group']
            schedule = storage.get_schedule(group=group)
        elif storage.get_vk_user(chat_id=chat_id)['course'] == 'None':
            group = storage.get_vk_user(chat_id=chat_id)['group']
            schedule = storage.get_schedule_prep(group=group)
        if not schedule:
            schedule_processing.sending_schedule_is_not_available(ans=ans)
            statistics.add(action='Расписание на сегодня', storage=storage, tz=tz)
            return
        schedule = schedule['schedule']
        week = find_week()
        # Если курс нуль, тогда это преподаватель
        if storage.get_vk_user(chat_id=chat_id)['course'] != 'None':
            schedule_one_day = get_one_day_schedule_in_str(schedule=schedule, week=week)
        elif storage.get_vk_user(chat_id=chat_id)['course'] == 'None':
            schedule_one_day = get_one_day_schedule_in_str_prep(schedule=schedule, week=week)

        # Проверяем, что расписание сформировалось
        if isinstance(schedule_one_day, APIError):
            await schedule_processing.sending_schedule_is_not_available(ans=ans)
            return

        if not schedule_one_day:
            await ans.answer('Сегодня пар нет 😎')
            return
        await ans.answer(f'{schedule_one_day}')
        statistics.add(action='Расписание на сегодня', storage=storage, tz=tz)

    elif 'Расписание на завтра 🍎' == data and user.get('group'):
        # Если курс нуль, тогда это преподаватель
        if storage.get_vk_user(chat_id=chat_id)['course'] != 'None':
            group = storage.get_vk_user(chat_id=chat_id)['group']
            schedule = storage.get_schedule(group=group)
        elif storage.get_vk_user(chat_id=chat_id)['course'] == 'None':
            group = storage.get_vk_user(chat_id=chat_id)['group']
            schedule = storage.get_schedule_prep(group=group)
        if not schedule:
            await ans.answer('Расписание временно недоступно🚫😣\n'
                             'Попробуйте позже⏱', keyboard=keyboards.make_keyboard_start_menu())
            statistics.add(action='Расписание на завтра', storage=storage, tz=tz)
            return
        schedule = schedule['schedule']
        week = find_week()
        if datetime.today().isoweekday() == 7:
            if week == 'odd':
                week = 'even'
            elif week == 'even':
                week = 'odd'
            else:
                week = 'all'

        if storage.get_vk_user(chat_id=chat_id)['course'] != 'None':
            schedule_next_day = get_next_day_schedule_in_str(schedule=schedule, week=week)
        elif storage.get_vk_user(chat_id=chat_id)['course'] == 'None':
            schedule_next_day = get_next_day_schedule_in_str_prep(schedule=schedule, week=week)

        # Проверяем, что расписание сформировалось
        if isinstance(schedule_next_day, APIError):
            await schedule_processing.sending_schedule_is_not_available(ans=ans)
            return

        if not schedule_next_day:
            await ans.answer('Завтра пар нет 😎')
            return
        await ans.answer(f'{schedule_next_day}')
        statistics.add(action='Расписание на завтра', storage=storage, tz=tz)

    elif 'Ближайшая пара ⏱' in data and user.get('group'):
        await ans.answer('Ближайшая пара', keyboard=keyboards.make_keyboard_nearlesson())
        statistics.add(action='Ближайшая пара', storage=storage, tz=tz)
        return


    elif 'Текущая' in data and user.get('group'):
        if storage.get_vk_user(chat_id=chat_id)['course'] != 'None':
            group = storage.get_vk_user(chat_id=chat_id)['group']
            schedule = storage.get_schedule(group=group)
        elif storage.get_vk_user(chat_id=chat_id)['course'] == 'None':
            group = storage.get_vk_user(chat_id=chat_id)['group']
            schedule = storage.get_schedule_prep(group=group)
        if not schedule:
            await ans.answer('Расписание временно недоступно🚫😣\n'
                             'Попробуйте позже⏱', keyboard=keyboards.make_keyboard_start_menu())
            statistics.add(action='Текущая', storage=storage, tz=tz)
            return
        schedule = schedule['schedule']
        week = find_week()

        now_lessons = get_now_lesson(schedule=schedule, week=week)

        # Проверяем, что расписание сформировалось
        if isinstance(now_lessons, APIError):
            await schedule_processing.sending_schedule_is_not_available(ans=ans)
            return

        # если пар нет
        if not now_lessons:
            await ans.answer('Сейчас пары нет, можете отдохнуть)', keyboard=keyboards.make_keyboard_start_menu())
            statistics.add(action='Текущая', storage=storage, tz=tz)
            return

        # Студент
        if storage.get_vk_user(chat_id=chat_id)['course'] != 'None':
            now_lessons_str = get_now_lesson_in_str_stud(now_lessons)

        # Преподаватель
        elif storage.get_vk_user(chat_id=chat_id)['course'] == 'None':
            now_lessons_str = get_now_lesson_in_str_prep(now_lessons)

        # Проверяем, что расписание сформировалось
        if isinstance(now_lessons_str, APIError):
            await schedule_processing.sending_schedule_is_not_available(ans=ans)
            return

        await ans.answer(f'🧠Текущая пара🧠\n'f'{now_lessons_str}', keyboard=keyboards.make_keyboard_start_menu())

        statistics.add(action='Текущая', storage=storage, tz=tz)

    elif 'Следующая' in data and user.get('group'):
        if storage.get_vk_user(chat_id=chat_id)['course'] != 'None':
            group = storage.get_vk_user(chat_id=chat_id)['group']
            schedule = storage.get_schedule(group=group)
        elif storage.get_vk_user(chat_id=chat_id)['course'] == 'None':
            group = storage.get_vk_user(chat_id=chat_id)['group']
            schedule = storage.get_schedule_prep(group=group)
        if not schedule:
            await ans.answer('Расписание временно недоступно🚫😣\n'
                             'Попробуйте позже⏱', keyboard=keyboards.make_keyboard_start_menu())
            statistics.add(action='Следующая', storage=storage, tz=tz)
            return
        schedule = schedule['schedule']
        week = find_week()

        near_lessons = get_near_lesson(schedule=schedule, week=week)

        # Проверяем, что расписание сформировалось
        if isinstance(near_lessons, APIError):
            await schedule_processing.sending_schedule_is_not_available(ans=ans)
            return

        # если пар нет
        if not near_lessons:
            await ans.answer('Сегодня больше пар нет 😎', keyboard=keyboards.make_keyboard_start_menu())
            statistics.add(action='Следующая', storage=storage, tz=tz)
            return

        # Студент
        if storage.get_vk_user(chat_id=chat_id)['course'] != 'None':
            near_lessons_str = get_now_lesson_in_str_stud(near_lessons)

        # Преподаватель
        elif storage.get_vk_user(chat_id=chat_id)['course'] == 'None':
            near_lessons_str = get_now_lesson_in_str_prep(near_lessons)

        # Проверяем, что расписание сформировалось
        if isinstance(near_lessons_str, APIError):
            await schedule_processing.sending_schedule_is_not_available(ans=ans)
            return

        await ans.answer(f'🧠Ближайшая пара🧠\n'f'{near_lessons_str}',
                         keyboard=keyboards.make_keyboard_start_menu())

        statistics.add(action='Следующая', storage=storage, tz=tz)
