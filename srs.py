from datetime import datetime, timedelta

from util import get_tz, today_str

MIN_EASE = 1.3


def _quality_from_rating(rating):
    """Переводит оценку пользователя в число качества SM-2 (0..5)."""
    if rating == "again":
        return 2
    if rating == "hard":
        return 3
    if rating == "easy":
        return 5
    return 3


def _add_days_to_today(days):
    """Возвращает дату YYYY-MM-DD через заданное число дней от сегодня."""
    current = datetime.now(get_tz())
    future = current + timedelta(days=days)
    return future.strftime("%Y-%m-%d")


def review(rating, repetitions, interval, ease):
    """Пересчитывает карточку по упрощённому SM-2.

    Возвращает кортеж (repetitions, interval, ease, due_date).
    rating — одно из: "again", "hard", "easy".
    """
    quality = _quality_from_rating(rating)

    if quality < 3:
        new_repetitions = 0
        new_interval = 1
    else:
        if repetitions == 0:
            new_interval = 1
        elif repetitions == 1:
            new_interval = 6
        else:
            new_interval = round(interval * ease)
        new_repetitions = repetitions + 1

    new_ease = ease + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    if new_ease < MIN_EASE:
        new_ease = MIN_EASE

    due_date = _add_days_to_today(new_interval)
    return new_repetitions, new_interval, new_ease, due_date


def new_item_due_date():
    """Дата показа новой карточки — сегодня."""
    return today_str()
