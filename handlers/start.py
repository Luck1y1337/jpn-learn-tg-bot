from aiogram import F, Router, html
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

import database
import keyboards
from common import resolve_lang
from locales import get_all_translations, get_text

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Регистрирует пользователя и запускает онбординг или показывает меню."""
    await state.clear()
    user_id = message.from_user.id
    username = message.from_user.username
    await database.add_user(user_id, username)

    lang = await database.get_user_lang(user_id)
    if lang is None:
        await message.answer(
            get_text("ru", "choose_language"),
            reply_markup=keyboards.language_keyboard(),
        )
        return

    level = await database.get_user_level(user_id)
    if level is None:
        await message.answer(
            get_text(lang, "choose_level"),
            reply_markup=keyboards.level_keyboard(),
        )
        return

    await show_main_menu(message, lang)


async def show_main_menu(message, lang):
    """Показывает приветствие и главное меню."""
    name = html.quote(message.from_user.first_name)
    await message.answer(
        get_text(lang, "welcome", name=name),
        reply_markup=keyboards.main_menu_keyboard(lang),
    )


@router.callback_query(F.data.startswith("lang:"))
async def callback_choose_language(callback: CallbackQuery):
    """Сохраняет язык и переходит к выбору уровня или показывает меню."""
    lang = callback.data.split(":")[1]
    user_id = callback.from_user.id
    username = callback.from_user.username

    await database.add_user(user_id, username)
    await database.set_user_lang(user_id, lang)

    await callback.message.delete()

    level = await database.get_user_level(user_id)
    if level is None:
        await callback.message.answer(
            get_text(lang, "choose_level"),
            reply_markup=keyboards.level_keyboard(),
        )
    else:
        await show_main_menu_from_callback(callback, lang)
    await callback.answer()


@router.callback_query(F.data.startswith("setlevel:"))
async def callback_choose_level(callback: CallbackQuery):
    """Сохраняет уровень и показывает главное меню."""
    level = callback.data.split(":")[1]
    user_id = callback.from_user.id

    await database.set_user_level(user_id, level)
    lang = await resolve_lang(user_id)

    await callback.message.delete()
    await callback.message.answer(get_text(lang, "level_saved", level=level))
    await show_main_menu_from_callback(callback, lang)
    await callback.answer()


async def show_main_menu_from_callback(callback, lang):
    """Показывает приветствие и главное меню в ответ на callback."""
    name = html.quote(callback.from_user.first_name)
    await callback.message.answer(
        get_text(lang, "welcome", name=name),
        reply_markup=keyboards.main_menu_keyboard(lang),
    )


@router.message(Command("language"))
@router.message(F.text.in_(get_all_translations("btn_set_language")))
async def button_language(message: Message):
    """Показывает выбор языка (доступен и из меню настроек)."""
    lang = await resolve_lang(message.from_user.id)
    await message.answer(
        get_text(lang, "choose_language"),
        reply_markup=keyboards.language_keyboard(),
    )
