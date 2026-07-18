from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

import keyboards
from common import is_admin, resolve_lang
from locales import get_all_translations, get_text
from handlers import donate, grammar, quiz, settings, start, stats, study
from handlers.admin import PANEL_TITLE

router = Router()


async def show_hub(target, user_id):
    """Показывает инлайн-хаб со всеми разделами."""
    lang = await resolve_lang(user_id)
    await target.answer(
        get_text(lang, "hub_header"),
        reply_markup=keyboards.main_hub_keyboard(lang, is_admin(user_id)),
    )


@router.message(Command("menu"))
@router.message(F.text.in_(get_all_translations("btn_menu")))
async def cmd_menu(message: Message):
    """Команда /menu и кнопка-лаунчер «☰ Меню» — открывают хаб."""
    await show_hub(message, message.from_user.id)


@router.callback_query(F.data == "menu:study")
async def hub_study(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await study.open_study(callback.message, callback.from_user.id, state)


@router.callback_query(F.data == "menu:quiz")
async def hub_quiz(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await quiz.open_quiz(callback.message, callback.from_user.id, state)


@router.callback_query(F.data == "menu:grammar")
async def hub_grammar(callback: CallbackQuery):
    await callback.answer()
    await grammar.open_grammar(callback.message, callback.from_user.id)


@router.callback_query(F.data == "menu:stats")
async def hub_stats(callback: CallbackQuery):
    await callback.answer()
    await stats.open_stats(callback.message, callback.from_user.id)


@router.callback_query(F.data == "menu:settings")
async def hub_settings(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await settings.open_settings(callback.message, callback.from_user.id, state)


@router.callback_query(F.data == "menu:donate")
async def hub_donate(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await donate.open_donate(callback.message, callback.from_user.id, state)


@router.callback_query(F.data == "menu:language")
async def hub_language(callback: CallbackQuery):
    await callback.answer()
    await start.open_language(callback.message, callback.from_user.id)


@router.callback_query(F.data == "menu:admin")
async def hub_admin(callback: CallbackQuery, state: FSMContext):
    """Открывает админ-панель из хаба (только для админа)."""
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    await state.clear()
    await callback.answer()
    await callback.message.answer(
        PANEL_TITLE, reply_markup=keyboards.admin_main_keyboard()
    )
