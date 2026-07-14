import database
from config import ADMIN_IDS, DEFAULT_LANG, JLPT_LEVELS


def is_admin(user_id):
    """Проверяет, что пользователь — администратор."""
    if user_id in ADMIN_IDS:
        return True
    return False


async def resolve_lang(user_id):
    """Возвращает язык пользователя или язык по умолчанию."""
    lang = await database.get_user_lang(user_id)
    if lang is None:
        return DEFAULT_LANG
    return lang


async def resolve_level(user_id):
    """Возвращает уровень пользователя или N5 по умолчанию."""
    level = await database.get_user_level(user_id)
    if level is None:
        return JLPT_LEVELS[0]
    return level
