from datetime import datetime


def add(action: str, storage, tz):
    """Схоранение статистики"""
    date_now = datetime.now(tz).strftime('%d.%m.%Y')
    time_now = datetime.now(tz).strftime('%H:%M')
    storage.save_vk_statistics(action=action, date=date_now, time=time_now)
