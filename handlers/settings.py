from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

import database
import keyboards
from common import resolve_lang
from config import (
    MAX_DAILY_COUNT,
    MIN_DAILY_COUNT,
    TIMEZONE,
)
from locales import get_all_translations, get_lang_name, get_text
from states import SettingsStates
from util import is_valid_time, normalize_time

router = Router()


async def render_settings(user_id, lang):
    """Формирует текст экрана настроек с текущими значениями."""
    user = await database.get_user(user_id)

    lang_name = get_lang_name(lang)

    level = user["level"]
    if level is None:
        level = "—"

    daily_time = user["daily_time"]
    if daily_time is None:
        daily_time = "—"

    daily_count = user["daily_count"]
    if daily_count is None:
        daily_count = "—"

    text = get_text(
        lang,
        "settings_title",
        lang=lang_name,
        level=level,
        time=daily_time,
        count=daily_count,
    )
    return text


@router.message(Command("settings"))
@router.message(F.text.in_(get_all_translations("btn_settings")))
async def open_settings(message: Message, state: FSMContext):
    """Показывает меню настроек."""
    await state.clear()
    user_id = message.from_user.id
    lang = await resolve_lang(user_id)
    text = await render_settings(user_id, lang)
    await message.answer(text, reply_markup=keyboards.settings_keyboard(lang))


@router.callback_query(F.data == "settings:lang")
async def callback_change_language(callback: CallbackQuery):
    """Открывает выбор языка интерфейса."""
    lang = await resolve_lang(callback.from_user.id)
    await callback.message.answer(
        get_text(lang, "choose_language"),
        reply_markup=keyboards.language_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "settings:level")
async def callback_change_level(callback: CallbackQuery):
    """Открывает выбор уровня JLPT."""
    lang = await resolve_lang(callback.from_user.id)
    await callback.message.answer(
        get_text(lang, "choose_level"),
        reply_markup=keyboards.level_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "settings:time")
async def callback_change_time(callback: CallbackQuery, state: FSMContext):
    """Просит ввести время ежедневной рассылки."""
    lang = await resolve_lang(callback.from_user.id)
    await state.set_state(SettingsStates.waiting_daily_time)
    await callback.message.answer(
        get_text(lang, "settings_enter_time", tz=TIMEZONE)
    )
    await callback.answer()


@router.message(SettingsStates.waiting_daily_time)
async def process_time(message: Message, state: FSMContext):
    """Проверяет и сохраняет время рассылки."""
    user_id = message.from_user.id
    lang = await resolve_lang(user_id)

    text = ""
    if message.text is not None:
        text = message.text.strip()

    if not is_valid_time(text):
        await message.answer(get_text(lang, "settings_time_invalid"))
        return

    normalized = normalize_time(text)
    await database.set_daily_time(user_id, normalized)
    await state.clear()
    await message.answer(
        get_text(lang, "settings_time_saved", time=normalized)
    )


@router.callback_query(F.data == "settings:count")
async def callback_change_count(callback: CallbackQuery, state: FSMContext):
    """Просит ввести количество новых слов в день."""
    lang = await resolve_lang(callback.from_user.id)
    await state.set_state(SettingsStates.waiting_daily_count)
    await callback.message.answer(
        get_text(
            lang,
            "settings_enter_count",
            min=MIN_DAILY_COUNT,
            max=MAX_DAILY_COUNT,
        )
    )
    await callback.answer()


@router.message(SettingsStates.waiting_daily_count)
async def process_count(message: Message, state: FSMContext):
    """Проверяет и сохраняет количество новых слов в день."""
    user_id = message.from_user.id
    lang = await resolve_lang(user_id)

    text = ""
    if message.text is not None:
        text = message.text.strip()

    if not text.isdigit():
        await message.answer(
            get_text(
                lang,
                "settings_count_invalid",
                min=MIN_DAILY_COUNT,
                max=MAX_DAILY_COUNT,
            )
        )
        return

    count = int(text)
    if count < MIN_DAILY_COUNT or count > MAX_DAILY_COUNT:
        await message.answer(
            get_text(
                lang,
                "settings_count_invalid",
                min=MIN_DAILY_COUNT,
                max=MAX_DAILY_COUNT,
            )
        )
        return

    await database.set_daily_count(user_id, count)
    await state.clear()
    await message.answer(
        get_text(lang, "settings_count_saved", count=count)
    )
