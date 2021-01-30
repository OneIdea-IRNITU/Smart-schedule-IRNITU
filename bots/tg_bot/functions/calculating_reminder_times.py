from datetime import timedelta, datetime


def calculating_reminder_times(schedule, time: int) -> list:
    """прощитывает время уведомления перед кадой парой"""
    reminders = []
    even = {}
    odd = {}
    # проходимся по дням в расписании
    for day in schedule:
        even[day['day']] = []
        odd[day['day']] = []
        # проходимся по парам
        # нужно добавить проверку на уже введенное время (например пара у двух подгрупп)!!!!!
        for lesson in day['lessons']:
            if lesson['name'] == 'свободно':
                continue
            # достаём время пары (часы и минуты)
            lesson_time = lesson['time'].split(':')
            h = int(lesson_time[0])
            m = int(lesson_time[-1])
            if lesson['week'] == 'even' or lesson['week'] == 'all':
                # расчитываем время до начала (время пары - время напоминания) и добавляем в список
                even[day['day']].append(str((timedelta(hours=h, minutes=m) - timedelta(minutes=time)))[:-3])

            if lesson['week'] == 'odd' or lesson['week'] == 'all':
                odd[day['day']].append(str((timedelta(hours=h, minutes=m) - timedelta(minutes=time)))[:-3])

    reminders = {
        'even': even,
        'odd': odd
    }

    return reminders
