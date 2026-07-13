from datetime import datetime
from zoneinfo import ZoneInfo

from config import TIMEZONE


def get_tz():
    """Возвращает объект часового пояса из настроек или UTC при ошибке."""
    try:
        return ZoneInfo(TIMEZONE)
    except Exception:
        return ZoneInfo("UTC")


def now_local():
    """Возвращает текущее время в выбранном часовом поясе."""
    return datetime.now(get_tz())


def today_str():
    """Возвращает сегодняшнюю дату в формате YYYY-MM-DD."""
    return now_local().strftime("%Y-%m-%d")


def now_hhmm():
    """Возвращает текущее время в формате HH:MM."""
    return now_local().strftime("%H:%M")


def is_valid_time(text):
    """Проверяет, что строка — корректное время в формате HH:MM."""
    if text is None:
        return False
    parts = text.split(":")
    if len(parts) != 2:
        return False
    hours_part = parts[0]
    minutes_part = parts[1]
    if not hours_part.isdigit():
        return False
    if not minutes_part.isdigit():
        return False
    hours = int(hours_part)
    minutes = int(minutes_part)
    if hours < 0 or hours > 23:
        return False
    if minutes < 0 or minutes > 59:
        return False
    return True


def normalize_time(text):
    """Приводит время к формату HH:MM с ведущими нулями."""
    parts = text.split(":")
    hours = int(parts[0])
    minutes = int(parts[1])
    result = "{:02d}:{:02d}".format(hours, minutes)
    return result


def days_between(earlier_date_str, later_date_str):
    """Возвращает число дней между двумя датами YYYY-MM-DD."""
    earlier = datetime.strptime(earlier_date_str, "%Y-%m-%d")
    later = datetime.strptime(later_date_str, "%Y-%m-%d")
    delta = later - earlier
    return delta.days
