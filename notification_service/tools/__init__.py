from datetime import datetime, timedelta


def forming_user_to_submit(
        chat_id: int,
        group: str,
        notifications: int,
        day_now: str,
        time_now: datetime,
        week: str) -> dict:
    """"""


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
