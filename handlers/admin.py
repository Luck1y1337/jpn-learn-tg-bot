import asyncio

from aiogram import F, Router, html
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

import database
import keyboards
from common import resolve_lang
from config import ADMIN_ID
from locales import get_text
from states import AdminStates

router = Router()


def is_admin(user_id):
    """Проверяет, что пользователь — администратор."""
    if ADMIN_ID == 0:
        return False
    if user_id == ADMIN_ID:
        return True
    return False


@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message, state: FSMContext):
    """Запускает создание рассылки (только для администратора)."""
    user_id = message.from_user.id
    lang = await resolve_lang(user_id)

    if not is_admin(user_id):
        await message.answer(get_text(lang, "adm_only"))
        return

    await state.set_state(AdminStates.waiting_broadcast)
    await message.answer(get_text(lang, "adm_bc_enter"))


@router.message(AdminStates.waiting_broadcast)
async def process_broadcast_text(message: Message, state: FSMContext):
    """Сохраняет текст рассылки и показывает подтверждение."""
    user_id = message.from_user.id
    lang = await resolve_lang(user_id)

    if not is_admin(user_id):
        await state.clear()
        return

    text = ""
    if message.text is not None:
        text = message.text.strip()

    if text == "":
        await message.answer(get_text(lang, "adm_bc_empty"))
        return

    await state.update_data(broadcast_text=message.text)
    users_count = await database.count_users()
    preview = html.quote(message.text)
    await message.answer(
        get_text(lang, "adm_bc_confirm", count=users_count, preview=preview),
        reply_markup=keyboards.broadcast_confirm_keyboard(lang),
    )


@router.callback_query(F.data == "admin:bc:cancel")
async def callback_broadcast_cancel(callback: CallbackQuery,
                                    state: FSMContext):
    """Отменяет рассылку."""
    lang = await resolve_lang(callback.from_user.id)
    await state.clear()
    await callback.message.edit_text(get_text(lang, "adm_bc_cancelled"))
    await callback.answer()


@router.callback_query(F.data == "admin:bc:send")
async def callback_broadcast_send(callback: CallbackQuery, state: FSMContext):
    """Рассылает сохранённое сообщение всем пользователям."""
    user_id = callback.from_user.id
    lang = await resolve_lang(user_id)

    if not is_admin(user_id):
        await callback.answer()
        return

    data = await state.get_data()
    text = data.get("broadcast_text")
    await state.clear()

    if text is None:
        await callback.message.edit_text(get_text(lang, "adm_bc_cancelled"))
        await callback.answer()
        return

    await callback.message.edit_text(get_text(lang, "adm_bc_started"))
    await callback.answer()

    user_ids = await database.get_all_user_ids()
    sent = 0
    failed = 0
    for target_id in user_ids:
        try:
            await callback.bot.send_message(target_id, text, parse_mode=None)
            sent = sent + 1
        except Exception:
            failed = failed + 1
        await asyncio.sleep(0.05)

    await callback.message.answer(
        get_text(lang, "adm_bc_done", sent=sent, failed=failed)
    )
