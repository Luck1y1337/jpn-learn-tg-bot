import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

import content_api
import database
import srs
from backup import perform_backup
from config import DEFAULT_DAILY_COUNT, DEFAULT_LANG
from locales import get_text
from util import get_tz, now_hhmm, today_str

logger = logging.getLogger(__name__)


def meaning_for(lang, item):
    """Возвращает значение из словаря контента на языке пользователя."""
    if lang == "ru":
        meaning = item.get("meaning_ru", "")
    elif lang == "uz":
        meaning = item.get("meaning_uz", "")
    else:
        meaning = item.get("meaning_en", "")

    if meaning is None or meaning == "":
        meaning = item.get("meaning_en", "")
    return meaning


def combine_readings(kanji):
    """Склеивает кунные и онные чтения кандзи в одну строку."""
    parts = []
    kun = kanji.get("kun_readings", "")
    on = kanji.get("on_readings", "")
    if kun is not None and kun != "":
        parts.append(kun)
    if on is not None and on != "":
        parts.append(on)
    return " / ".join(parts)


async def add_word_to_srs(user_id, word):
    """Добавляет слово из ежедневной рассылки в SRS пользователя."""
    due_date = srs.new_item_due_date()
    await database.add_srs_item(
        user_id,
        "word",
        word["word"],
        word["word"],
        word["reading"],
        word["meaning_ru"],
        word["meaning_en"],
        word["meaning_uz"],
        due_date,
    )


async def add_kanji_to_srs(user_id, kanji):
    """Добавляет кандзи из ежедневной рассылки в SRS пользователя."""
    due_date = srs.new_item_due_date()
    reading = combine_readings(kanji)
    await database.add_srs_item(
        user_id,
        "kanji",
        kanji["character"],
        kanji["character"],
        reading,
        kanji["meaning_ru"],
        kanji["meaning_en"],
        kanji["meaning_uz"],
        due_date,
    )


async def build_and_send_daily(bot, user):
    """Собирает и отправляет ежедневную порцию материала одному пользователю."""
    user_id = user["user_id"]
    lang = user["lang"]
    if lang is None:
        lang = DEFAULT_LANG
    level = user["level"]
    if level is None:
        return

    count = user["daily_count"]
    if count is None:
        count = DEFAULT_DAILY_COUNT

    words = await content_api.get_random_words(level, count)
    kanji_list = await content_api.get_random_kanji(level, 1)
    grammar = await database.get_random_grammar(level)

    for word in words:
        await add_word_to_srs(user_id, word)
    for kanji in kanji_list:
        await add_kanji_to_srs(user_id, kanji)

    text = get_text(lang, "daily_title") + "\n\n"

    if len(words) > 0:
        text = text + get_text(lang, "daily_words_header") + "\n"
        for word in words:
            meaning = meaning_for(lang, word)
            text = text + get_text(
                lang,
                "daily_word_line",
                word=word["word"],
                reading=word["reading"],
                meaning=meaning,
            ) + "\n"
        text = text + "\n"

    if len(kanji_list) > 0:
        text = text + get_text(lang, "daily_kanji_header") + "\n"
        for kanji in kanji_list:
            meaning = meaning_for(lang, kanji)
            text = text + get_text(
                lang,
                "daily_kanji_line",
                character=kanji["character"],
                meaning=meaning,
            ) + "\n"
        text = text + "\n"

    if grammar is not None:
        text = text + get_text(lang, "daily_grammar_header") + "\n"
        text = text + get_text(
            lang,
            "daily_grammar_line",
            title=grammar["title"],
            structure=grammar["structure"],
        ) + "\n\n"

    text = text + get_text(lang, "daily_footer")

    try:
        await bot.send_message(user_id, text)
    except Exception as error:
        logger.warning("Не удалось отправить рассылку %s: %s", user_id, error)


async def daily_tick(bot):
    """Раз в минуту проверяет, кому пора отправить ежедневную рассылку."""
    current_time = now_hhmm()
    today = today_str()

    users = await database.get_all_users()
    for user in users:
        if user["lang"] is None:
            continue
        if user["level"] is None:
            continue
        if user["daily_time"] != current_time:
            continue
        if user["last_daily_date"] == today:
            continue

        await database.set_last_daily_date(user["user_id"], today)
        await build_and_send_daily(bot, user)


def start_scheduler(bot):
    """Создаёт и запускает планировщик ежедневной рассылки."""
    scheduler = AsyncIOScheduler(timezone=get_tz())
    scheduler.add_job(
        daily_tick,
        "interval",
        minutes=1,
        args=[bot],
        max_instances=1,
        misfire_grace_time=30,
    )
    scheduler.add_job(
        perform_backup,
        "cron",
        hour=3,
        minute=0,
        args=[bot],
        max_instances=1,
        misfire_grace_time=300,
    )
    scheduler.start()
    return scheduler
