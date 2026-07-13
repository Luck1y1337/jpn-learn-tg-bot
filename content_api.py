import logging

import aiohttp

import database
from config import HTTP_TIMEOUT, KANJI_API_BASE, VOCAB_API_BASE
from translate import translate_to_ru_uz

logger = logging.getLogger(__name__)


def level_to_number(level):
    """Переводит уровень вида "N5" в число 5 для параметров API."""
    digits = level.replace("N", "")
    if digits.isdigit():
        return int(digits)
    return 5


async def _get_json(url):
    """Выполняет GET-запрос и возвращает JSON или None при ошибке."""
    timeout = aiohttp.ClientTimeout(total=HTTP_TIMEOUT)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                if response.status != 200:
                    logger.warning("API %s вернул статус %s", url,
                                   response.status)
                    return None
                data = await response.json()
                return data
    except Exception as error:
        logger.warning("Ошибка запроса к %s: %s", url, error)
        return None


# ---------------------------------------------------------------------------
# Слова
# ---------------------------------------------------------------------------


async def _cache_word(raw, level):
    """Кэширует слово с переводом и возвращает нормализованный словарь."""
    word = raw.get("word")
    if word is None or word == "":
        return None

    cached = await database.get_word(word)
    if cached is not None:
        return _word_row_to_dict(cached)

    meaning_en = raw.get("meaning", "")
    reading = raw.get("furigana", "")
    romaji = raw.get("romaji", "")

    meaning_ru, meaning_uz = await translate_to_ru_uz(meaning_en)

    await database.upsert_word(
        word, level, reading, romaji, meaning_en, meaning_ru, meaning_uz
    )

    result = {
        "word": word,
        "level": level,
        "reading": reading,
        "romaji": romaji,
        "meaning_en": meaning_en,
        "meaning_ru": meaning_ru,
        "meaning_uz": meaning_uz,
    }
    return result


def _word_row_to_dict(row):
    """Преобразует строку кэша слова в словарь."""
    result = {
        "word": row["word"],
        "level": row["level"],
        "reading": row["reading"],
        "romaji": row["romaji"],
        "meaning_en": row["meaning_en"],
        "meaning_ru": row["meaning_ru"],
        "meaning_uz": row["meaning_uz"],
    }
    return result


async def get_random_words(level, count):
    """Возвращает до count различных слов уровня (с кэшированием).

    Тянет случайные слова с jlpt-vocab-api, переводит и кэширует новые.
    """
    number = level_to_number(level)
    url = VOCAB_API_BASE + "/words/random?level=" + str(number)

    result = []
    seen_words = []
    attempts = 0
    max_attempts = count * 4 + 5

    while len(result) < count and attempts < max_attempts:
        attempts = attempts + 1
        raw = await _get_json(url)
        if raw is None:
            continue
        word = raw.get("word")
        if word is None:
            continue
        if word in seen_words:
            continue
        seen_words.append(word)
        word_dict = await _cache_word(raw, level)
        if word_dict is not None:
            result.append(word_dict)

    return result


async def ensure_words_cached(level, min_count):
    """Гарантирует, что в кэше есть хотя бы min_count слов уровня."""
    have = await database.count_cached_words(level)
    if have >= min_count:
        return
    need = min_count - have
    await get_random_words(level, need)


# ---------------------------------------------------------------------------
# Кандзи
# ---------------------------------------------------------------------------


def _kanji_row_to_dict(row):
    """Преобразует строку кэша кандзи в словарь."""
    result = {
        "character": row["character"],
        "level": row["jlpt_level"],
        "meaning_en": row["meaning_en"],
        "meaning_ru": row["meaning_ru"],
        "meaning_uz": row["meaning_uz"],
        "kun_readings": row["kun_readings"],
        "on_readings": row["on_readings"],
        "stroke_count": row["stroke_count"],
    }
    return result


async def get_kanji_detail(character, level):
    """Возвращает подробности по кандзи (с кэшированием)."""
    cached = await database.get_kanji(character)
    if cached is not None:
        return _kanji_row_to_dict(cached)

    url = KANJI_API_BASE + "/kanji/" + character
    raw = await _get_json(url)
    if raw is None:
        return None

    meanings = raw.get("meanings", [])
    meaning_en = ", ".join(meanings)

    kun_list = raw.get("kun_readings", [])
    on_list = raw.get("on_readings", [])
    kun_readings = ", ".join(kun_list)
    on_readings = ", ".join(on_list)
    stroke_count = raw.get("stroke_count", 0)

    meaning_ru, meaning_uz = await translate_to_ru_uz(meaning_en)

    await database.upsert_kanji(
        character, level, meaning_en, meaning_ru, meaning_uz,
        kun_readings, on_readings, stroke_count
    )

    result = {
        "character": character,
        "level": level,
        "meaning_en": meaning_en,
        "meaning_ru": meaning_ru,
        "meaning_uz": meaning_uz,
        "kun_readings": kun_readings,
        "on_readings": on_readings,
        "stroke_count": stroke_count,
    }
    return result


async def get_kanji_list_for_level(level):
    """Возвращает список символов кандзи для уровня JLPT или пустой список."""
    number = level_to_number(level)
    url = KANJI_API_BASE + "/kanji/jlpt-" + str(number)
    data = await _get_json(url)
    if data is None:
        return []
    if not isinstance(data, list):
        return []
    return data


async def get_random_kanji(level, count):
    """Возвращает до count случайных кандзи уровня (с подробностями)."""
    import random

    characters = await get_kanji_list_for_level(level)
    if len(characters) == 0:
        return []

    shuffled = list(characters)
    random.shuffle(shuffled)

    result = []
    index = 0
    while len(result) < count and index < len(shuffled):
        character = shuffled[index]
        index = index + 1
        detail = await get_kanji_detail(character, level)
        if detail is not None:
            result.append(detail)

    return result
