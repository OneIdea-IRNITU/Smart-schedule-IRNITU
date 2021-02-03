from datetime import datetime, timedelta


def find_week():
    """Определение текущей недели"""
    now = datetime.now()
    sep = datetime(now.year if now.month >= 9 else now.year - 1, 9, 1)
    d1 = sep - timedelta(days=sep.weekday())
    d2 = now - timedelta(days=now.weekday())

    parity = ((d2 - d1).days // 7) % 2
    return 'odd' if parity else 'even'


def forming_user_to_submit(
        chat_id: int,
        group: str,
        notifications: int,
        day_now: str,
        time_now: datetime,
        week: str) -> dict:
    """Формирование информации о пользователе для отправки"""

    # определяем фактическое время пары (прибавляем к текущему времени время напоминания)
    lesson_time = (time_now + timedelta(minutes=notifications)).strftime('%H:%M')

    user = {
        'chat_id': chat_id,
        'group': group,
        'week': week,
        'day': day_now,
        'notifications': notifications,
        'time': lesson_time
    }

    return user


def check_the_reminder_time(time_now, user_day_reminder_time: list) -> bool:
    """Проверка, что у пользователя влючено напоминание на текущее время"""
    hours_now = int(time_now.strftime('%H'))
    minutes_now = time_now.strftime('%M')

    return user_day_reminder_time and f'{hours_now}:{minutes_now}' in user_day_reminder_time
