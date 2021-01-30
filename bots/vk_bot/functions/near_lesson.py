from datetime import datetime, timedelta
import platform
import locale
import pytz

TZ_IRKUTSK = pytz.timezone('Asia/Irkutsk')
locale_name = ('ru_RU.UTF-8' if platform.system() == 'Linux' else 'ru_RU')
locale.setlocale(locale.LC_TIME, locale_name)


def get_near_lesson(schedule: list, week: str) -> list:
    """Возвращает ближайшую пару"""

    day_now = datetime.now(TZ_IRKUTSK).strftime('%A')
    hours_now = int(datetime.now(TZ_IRKUTSK).strftime('%H'))
    minutes_now = int(datetime.now(TZ_IRKUTSK).strftime('%M'))

    lessons = {}
    # находим текущий день
    for one_day in schedule:
        if one_day['day'].lower() == day_now.lower():
            lessons = one_day['lessons']
            break
    # если сегодняшнего дня нет в расписании значит пар сегодня нет
    if not lessons:
        return

    near_lessons = []
    for lesson in lessons:
        lesson_week = lesson['week']
        # смотрим только на пары из текущей недели
        if lesson_week != week and lesson_week != 'all':
            continue

        hours_lesson, minutes_lesson = map(int, lesson['time'].split(':'))
        # находим ближайшую пару
        if (hours_lesson * 60 + minutes_lesson) - (hours_now * 60 + minutes_now) >= 0 and not near_lessons:
            near_lessons.append(lesson)
        # если несколько пар в одно время (у разных подгрупп)
        elif near_lessons:
            if lesson['time'] == near_lessons[0]['time']:
                near_lessons.append(lesson)


    return near_lessons

def get_now_lesson(schedule: list, week: str) -> list:
    """"Возвращает текущую пару"""

    day_now = datetime.now(TZ_IRKUTSK).strftime('%A')
    hours_now = int(datetime.now(TZ_IRKUTSK).strftime('%H'))
    minutes_now = int(datetime.now(TZ_IRKUTSK).strftime('%M'))

    lessons = {}
    # находим текущий день
    for one_day in schedule:
        if one_day['day'].lower() == day_now.lower():
            lessons = one_day['lessons']
            break
    # если сегодняшнего дня нет в расписании значит пар сегодня нет
    if not lessons:
        return

    now_lessons = []
    for lesson in lessons:
        lesson_week = lesson['week']
        # смотрим только на пары из текущей недели
        if lesson_week != week and lesson_week != 'all':
            continue

        hours_lesson, minutes_lesson = map(int, lesson['time'].split(':'))
        # находим ближайшую пару
        a = hours_lesson * 60 + minutes_lesson
        b = hours_now * 60 + minutes_now
        if 0 <= b - a <= 90 and not now_lessons:
            now_lessons.append(lesson)
        # если несколько пар в одно время (у разных подгрупп)
        elif now_lessons:
            if lesson['time'] == now_lessons[0]['time']:
                now_lessons.append(lesson)

    return now_lessons
