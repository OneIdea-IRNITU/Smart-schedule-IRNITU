from datetime import datetime, timedelta
import pytz

TZ_IRKUTSK = pytz.timezone('Asia/Irkutsk')


def find_week():
    now = datetime.now(TZ_IRKUTSK)

    sep = datetime(now.year if now.month >= 9 else now.year - 1, 9, 1, tzinfo=TZ_IRKUTSK)

    d1 = sep - timedelta(days=sep.weekday())
    d2 = now - timedelta(days=now.weekday())
    parity = ((d2 - d1).days // 7) % 2
    return 'odd' if parity else 'even'