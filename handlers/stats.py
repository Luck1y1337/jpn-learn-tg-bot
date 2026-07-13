from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

import database
from common import resolve_lang, resolve_level
from locales import get_all_translations, get_text
from util import today_str

router = Router()


@router.message(Command("stats"))
@router.message(F.text.in_(get_all_translations("btn_stats")))
async def show_stats(message: Message):
    """Показывает прогресс пользователя: карточки, стрик, квизы."""
    user_id = message.from_user.id
    lang = await resolve_lang(user_id)
    level = await resolve_level(user_id)

    user = await database.get_user(user_id)
    streak = 0
    if user is not None and user["streak"] is not None:
        streak = user["streak"]

    today = today_str()
    total = await database.count_total_srs(user_id)
    learned = await database.count_learned(user_id)
    due = await database.count_due_items(user_id, today)

    quiz_count, quiz_correct, quiz_total = await database.get_quiz_stats(
        user_id
    )

    if quiz_total > 0:
        accuracy = round(quiz_correct * 100 / quiz_total)
    else:
        accuracy = 0

    text = get_text(lang, "stats_title") + "\n\n"
    text = text + get_text(
        lang,
        "stats_body",
        level=level,
        streak=streak,
        total=total,
        learned=learned,
        due=due,
        quiz_count=quiz_count,
        accuracy=accuracy,
    )
    await message.answer(text)
