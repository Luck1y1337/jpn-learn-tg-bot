from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

import database
import keyboards
import srs
from common import resolve_lang
from locales import get_all_translations, get_text
from util import today_str

router = Router()

DUE_LIMIT = 50


def pick_meaning(lang, item):
    """Возвращает значение карточки на языке пользователя (с запасным EN)."""
    if lang == "ru":
        meaning = item["meaning_ru"]
    elif lang == "uz":
        meaning = item["meaning_uz"]
    else:
        meaning = item["meaning_en"]

    if meaning is None or meaning == "":
        meaning = item["meaning_en"]
    return meaning


def render_front(lang, item):
    """Формирует текст лицевой стороны карточки."""
    return get_text(lang, "study_front", front=item["front"])


def render_back(lang, item):
    """Формирует текст обратной стороны карточки: чтение и значение."""
    meaning = pick_meaning(lang, item)
    reading = item["reading"]

    text = "🃏 <b>" + item["front"] + "</b>\n\n"
    if reading is not None and reading != "":
        text = text + get_text(lang, "study_reading_label") + ": " + reading
        text = text + "\n"
    text = text + get_text(lang, "study_meaning_label") + ": " + meaning
    text = text + "\n\n" + get_text(lang, "study_rate_prompt")
    return text


async def open_study(target, user_id, state):
    """Начинает сессию повторения SRS. Общее ядро для команды и инлайн-хаба.

    target — объект с методом .answer() (Message или callback.message).
    """
    await state.clear()
    lang = await resolve_lang(user_id)

    today = today_str()
    due_items = await database.get_due_items(user_id, today, 1)
    if len(due_items) == 0:
        await target.answer(get_text(lang, "study_no_due"))
        return

    await state.update_data(reviewed=0)
    item = due_items[0]
    await target.answer(
        render_front(lang, item),
        reply_markup=keyboards.study_show_answer_keyboard(lang, item["id"]),
    )


@router.message(Command("study"))
@router.message(F.text.in_(get_all_translations("btn_study")))
async def start_study(message: Message, state: FSMContext):
    """Команда /study и кнопка меню — открывают сессию повторения."""
    await open_study(message, message.from_user.id, state)


@router.callback_query(F.data.startswith("study:show:"))
async def callback_show_answer(callback: CallbackQuery):
    """Показывает обратную сторону карточки и кнопки оценки."""
    item_id = int(callback.data.split(":")[2])
    lang = await resolve_lang(callback.from_user.id)

    item = await database.get_srs_item(item_id)
    if item is None:
        await callback.answer()
        return

    await callback.message.edit_text(
        render_back(lang, item),
        reply_markup=keyboards.study_rating_keyboard(lang, item_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("study:rate:"))
async def callback_rate(callback: CallbackQuery, state: FSMContext):
    """Пересчитывает карточку по оценке и показывает следующую."""
    parts = callback.data.split(":")
    item_id = int(parts[2])
    rating = parts[3]

    user_id = callback.from_user.id
    lang = await resolve_lang(user_id)

    item = await database.get_srs_item(item_id)
    if item is None:
        await callback.answer()
        return

    new_repetitions, new_interval, new_ease, due_date = srs.review(
        rating, item["repetitions"], item["interval"], item["ease"]
    )
    await database.update_srs_item(
        item_id, new_interval, new_ease, new_repetitions, due_date
    )

    data = await state.get_data()
    reviewed = data.get("reviewed", 0) + 1
    await state.update_data(reviewed=reviewed)

    today = today_str()
    due_items = await database.get_due_items(user_id, today, 1)
    if len(due_items) == 0:
        await update_streak(user_id, today)
        await state.clear()
        await callback.message.edit_text(
            get_text(lang, "study_done", count=reviewed)
        )
        await callback.answer()
        return

    next_item = due_items[0]
    await callback.message.edit_text(
        render_front(lang, next_item),
        reply_markup=keyboards.study_show_answer_keyboard(
            lang, next_item["id"]
        ),
    )
    await callback.answer()


async def update_streak(user_id, today):
    """Обновляет стрик пользователя после завершения сессии."""
    user = await database.get_user(user_id)
    if user is None:
        return

    last_date = user["last_study_date"]
    current_streak = user["streak"]
    if current_streak is None:
        current_streak = 0

    if last_date == today:
        return

    if last_date is None:
        new_streak = 1
    else:
        from util import days_between

        gap = days_between(last_date, today)
        if gap == 1:
            new_streak = current_streak + 1
        else:
            new_streak = 1

    await database.set_streak(user_id, new_streak, today)
