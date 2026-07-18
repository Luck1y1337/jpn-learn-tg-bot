import json

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

import database
import keyboards
from common import resolve_lang, resolve_level
from locales import get_all_translations, get_text

router = Router()


def pick_explanation(lang, row):
    """Возвращает объяснение грамматики на языке пользователя."""
    if lang == "ru":
        explanation = row["explanation_ru"]
    elif lang == "uz":
        explanation = row["explanation_uz"]
    else:
        explanation = row["explanation_en"]

    if explanation is None or explanation == "":
        explanation = row["explanation_en"]
    return explanation


def pick_example_translation(lang, example):
    """Возвращает перевод примера на языке пользователя."""
    if lang == "ru":
        translation = example.get("ru", "")
    elif lang == "uz":
        translation = example.get("uz", "")
    else:
        translation = example.get("en", "")

    if translation is None or translation == "":
        translation = example.get("en", "")
    return translation


def render_examples(lang, examples_json):
    """Формирует блок примеров для карточки грамматики."""
    try:
        examples = json.loads(examples_json)
    except Exception:
        examples = []

    lines = []
    for example in examples:
        jp = example.get("jp", "")
        translation = pick_example_translation(lang, example)
        line = "• " + jp + "\n  <i>" + translation + "</i>"
        lines.append(line)

    return "\n".join(lines)


def render_grammar(lang, row):
    """Формирует текст карточки грамматики."""
    explanation = pick_explanation(lang, row)
    examples_text = render_examples(lang, row["examples"])
    text = get_text(
        lang,
        "grammar_card",
        title=row["title"],
        level=row["level"],
        structure=row["structure"],
        explanation=explanation,
        examples=examples_text,
    )
    return text


async def open_grammar(target, user_id):
    """Показывает первую грамматическую конструкцию текущего уровня.

    Общее ядро для команды и инлайн-хаба.
    """
    lang = await resolve_lang(user_id)
    level = await resolve_level(user_id)

    rows = await database.get_grammar_by_level(level)
    if len(rows) == 0:
        await target.answer(get_text(lang, "grammar_none"))
        return

    row = rows[0]
    await target.answer(
        render_grammar(lang, row),
        reply_markup=keyboards.grammar_nav_keyboard(lang, 0, len(rows)),
    )


@router.message(Command("grammar"))
@router.message(F.text.in_(get_all_translations("btn_grammar")))
async def start_grammar(message: Message):
    """Команда /grammar и кнопка меню — открывают грамматику."""
    await open_grammar(message, message.from_user.id)


@router.callback_query(F.data.startswith("grammar:nav:"))
async def callback_navigate(callback: CallbackQuery):
    """Листает грамматические карточки вперёд и назад."""
    index = int(callback.data.split(":")[2])
    user_id = callback.from_user.id
    lang = await resolve_lang(user_id)
    level = await resolve_level(user_id)

    rows = await database.get_grammar_by_level(level)
    if len(rows) == 0:
        await callback.answer()
        return
    if index < 0 or index >= len(rows):
        await callback.answer()
        return

    row = rows[index]
    await callback.message.edit_text(
        render_grammar(lang, row),
        reply_markup=keyboards.grammar_nav_keyboard(lang, index, len(rows)),
    )
    await callback.answer()


@router.callback_query(F.data == "grammar:noop")
async def callback_noop(callback: CallbackQuery):
    """Пустой обработчик для счётчика в навигации."""
    await callback.answer()
