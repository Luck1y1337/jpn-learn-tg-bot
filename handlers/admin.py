import asyncio
import os
import platform
import shutil
import time
import zipfile

import psutil
from aiogram import Bot, F, Router, html
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

import database
import keyboards
from backup import perform_backup
from common import is_admin, resolve_lang
from locales import get_text
from states import AdminStates

router = Router()

USERS_PAGE_SIZE = 10
PANEL_TITLE = "👑 <b>Админ-панель</b>\n━━━━━━━━━━━━━━"
# Куда стейджим загруженный бэкап (уже как .db) до подтверждения восстановления.
RESTORE_READY = "cache/backup/restore_ready.db"


# ---------------------------------------------------------------------------
# Вход в панель
# ---------------------------------------------------------------------------


@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    """Открывает админ-панель (только для администратора)."""
    if not is_admin(message.from_user.id):
        return
    await state.clear()
    await message.answer(
        PANEL_TITLE, reply_markup=keyboards.admin_main_keyboard()
    )


@router.callback_query(F.data == "admin:main")
async def cb_admin_main(callback: CallbackQuery, state: FSMContext):
    """Возвращает в главное меню панели."""
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    await state.clear()
    await callback.message.edit_text(
        PANEL_TITLE, reply_markup=keyboards.admin_main_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "admin:close")
async def cb_admin_close(callback: CallbackQuery, state: FSMContext):
    """Закрывает панель."""
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    await state.clear()
    await callback.message.edit_text("✖️ Панель закрыта.")
    await callback.answer()


# ---------------------------------------------------------------------------
# Статистика
# ---------------------------------------------------------------------------


@router.callback_query(F.data == "admin:stats")
async def cb_admin_stats(callback: CallbackQuery):
    """Показывает сводную статистику по боту."""
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return

    total_users = await database.count_users()
    blocked = await database.count_blocked_users()
    by_level = await database.count_users_by_level()
    by_lang = await database.count_users_by_lang()
    srs_total = await database.count_all_srs()
    quizzes = await database.count_all_quizzes()
    don_count, don_sum = await database.get_donations_summary()
    words = await database.count_all_cached_words()
    kanji = await database.count_all_cached_kanji()
    grammar = await database.count_all_grammar()

    level_parts = []
    for level in ["N5", "N4", "N3", "N2", "N1"]:
        count = by_level.get(level, 0)
        level_parts.append(level + ": " + str(count))
    level_line = ", ".join(level_parts)

    lang_parts = []
    for lang_code in ["ru", "en", "uz"]:
        count = by_lang.get(lang_code, 0)
        lang_parts.append(lang_code + ": " + str(count))
    lang_line = ", ".join(lang_parts)

    text = "📊 <b>Статистика</b>\n━━━━━━━━━━━━━━\n"
    text = text + "👥 Пользователей: <b>" + str(total_users) + "</b>\n"
    text = text + "🚫 Заблокировано: <b>" + str(blocked) + "</b>\n"
    text = text + "🎌 По уровням: " + level_line + "\n"
    text = text + "🌐 По языкам: " + lang_line + "\n\n"
    text = text + "📚 Карточек SRS: <b>" + str(srs_total) + "</b>\n"
    text = text + "📝 Квизов пройдено: <b>" + str(quizzes) + "</b>\n\n"
    text = text + "⭐️ Донатов: <b>" + str(don_count) + "</b> на <b>"
    text = text + str(don_sum) + "</b>\n\n"
    text = text + "🗄 Кэш слов: <b>" + str(words) + "</b>\n"
    text = text + "🈶 Кэш кандзи: <b>" + str(kanji) + "</b>\n"
    text = text + "📖 Грамматики: <b>" + str(grammar) + "</b>"

    await callback.message.edit_text(
        text, reply_markup=keyboards.admin_back_keyboard("admin:main")
    )
    await callback.answer()


# ---------------------------------------------------------------------------
# Пользователи
# ---------------------------------------------------------------------------


def render_user_line(number, user):
    """Формирует одну строку списка пользователей."""
    username = user["username"]
    if username is not None and username != "":
        name = "@" + username
    else:
        name = "id " + str(user["user_id"])

    level = user["level"]
    if level is None:
        level = "—"
    lang = user["lang"]
    if lang is None:
        lang = "—"
    streak = user["streak"]
    if streak is None:
        streak = 0

    line = str(number) + ". " + name + " (" + str(user["user_id"]) + ")"
    line = line + " — " + level + "/" + lang + " 🔥" + str(streak)
    if user["is_blocked"] == 1:
        line = line + " 🚫"
    return line


@router.callback_query(F.data.startswith("admin:users:"))
async def cb_admin_users(callback: CallbackQuery):
    """Показывает страницу списка пользователей."""
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return

    offset = int(callback.data.split(":")[2])
    rows = await database.get_users_page(offset, USERS_PAGE_SIZE + 1)

    has_next = len(rows) > USERS_PAGE_SIZE
    page_rows = rows[:USERS_PAGE_SIZE]

    total = await database.count_users()
    text = "👥 <b>Пользователи</b> (всего " + str(total) + ")\n"
    text = text + "━━━━━━━━━━━━━━\n"

    if len(page_rows) == 0:
        text = text + "Пусто."
    else:
        number = offset + 1
        for user in page_rows:
            text = text + render_user_line(number, user) + "\n"
            number = number + 1

    await callback.message.edit_text(
        text,
        reply_markup=keyboards.admin_users_keyboard(
            offset, USERS_PAGE_SIZE, has_next
        ),
    )
    await callback.answer()


@router.callback_query(F.data == "admin:users_search")
async def cb_admin_users_search(callback: CallbackQuery, state: FSMContext):
    """Просит ввести ID или username для поиска."""
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    await state.set_state(AdminStates.waiting_user_search)
    await callback.message.answer(
        "🔍 Пришли ID пользователя или часть username для поиска."
    )
    await callback.answer()


@router.message(AdminStates.waiting_user_search)
async def process_user_search(message: Message, state: FSMContext):
    """Ищет пользователей и показывает результаты."""
    if not is_admin(message.from_user.id):
        await state.clear()
        return

    query = ""
    if message.text is not None:
        query = message.text.strip()
    await state.clear()

    if query == "":
        await message.answer("⚠️ Пустой запрос.")
        return

    rows = await database.find_users(query)
    if len(rows) == 0:
        await message.answer(
            "😔 Никого не нашёл.",
            reply_markup=keyboards.admin_back_keyboard("admin:main"),
        )
        return

    text = "🔍 <b>Результаты поиска</b>\n━━━━━━━━━━━━━━\n"
    number = 1
    for user in rows:
        text = text + render_user_line(number, user) + "\n"
        number = number + 1

    await message.answer(
        text, reply_markup=keyboards.admin_back_keyboard("admin:main")
    )


# ---------------------------------------------------------------------------
# Бан / разбан
# ---------------------------------------------------------------------------


@router.callback_query(F.data == "admin:ban_menu")
async def cb_admin_ban_menu(callback: CallbackQuery):
    """Показывает меню блокировки."""
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    await callback.message.edit_text(
        "🔨 <b>Блокировка пользователей</b>\n━━━━━━━━━━━━━━\n"
        "Забаненные не смогут пользоваться ботом.",
        reply_markup=keyboards.admin_ban_menu_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "admin:ban")
async def cb_admin_ban(callback: CallbackQuery, state: FSMContext):
    """Просит ID пользователя для бана."""
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    await state.set_state(AdminStates.waiting_ban_id)
    await callback.message.answer("🔨 Пришли ID пользователя для бана.")
    await callback.answer()


@router.message(AdminStates.waiting_ban_id)
async def process_ban(message: Message, state: FSMContext):
    """Блокирует пользователя по ID."""
    if not is_admin(message.from_user.id):
        await state.clear()
        return

    text = ""
    if message.text is not None:
        text = message.text.strip()
    await state.clear()

    if not text.isdigit():
        await message.answer(
            "⚠️ Нужен числовой ID.",
            reply_markup=keyboards.admin_back_keyboard("admin:main"),
        )
        return

    target_id = int(text)
    await database.set_user_blocked(target_id, 1)
    await message.answer(
        "✅ Пользователь <code>" + str(target_id) + "</code> заблокирован.",
        reply_markup=keyboards.admin_back_keyboard("admin:main"),
    )


@router.callback_query(F.data == "admin:unban")
async def cb_admin_unban(callback: CallbackQuery, state: FSMContext):
    """Просит ID пользователя для разбана."""
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    await state.set_state(AdminStates.waiting_unban_id)
    await callback.message.answer("♻️ Пришли ID пользователя для разбана.")
    await callback.answer()


@router.message(AdminStates.waiting_unban_id)
async def process_unban(message: Message, state: FSMContext):
    """Снимает блокировку с пользователя по ID."""
    if not is_admin(message.from_user.id):
        await state.clear()
        return

    text = ""
    if message.text is not None:
        text = message.text.strip()
    await state.clear()

    if not text.isdigit():
        await message.answer(
            "⚠️ Нужен числовой ID.",
            reply_markup=keyboards.admin_back_keyboard("admin:main"),
        )
        return

    target_id = int(text)
    await database.set_user_blocked(target_id, 0)
    await message.answer(
        "✅ Пользователь <code>" + str(target_id) + "</code> разблокирован.",
        reply_markup=keyboards.admin_back_keyboard("admin:main"),
    )


# ---------------------------------------------------------------------------
# Настройки: система и бэкап
# ---------------------------------------------------------------------------


@router.callback_query(F.data == "admin:settings")
async def cb_admin_settings(callback: CallbackQuery):
    """Показывает меню настроек."""
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    await callback.message.edit_text(
        "⚙️ <b>Настройки</b>\n━━━━━━━━━━━━━━",
        reply_markup=keyboards.admin_settings_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "admin:sysinfo")
async def cb_admin_sysinfo(callback: CallbackQuery):
    """Показывает информацию о системе через psutil."""
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return

    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory().percent
    disk_path = os.path.abspath(os.sep)
    disk = psutil.disk_usage(disk_path).percent

    process = psutil.Process(os.getpid())
    uptime_seconds = int(time.time() - process.create_time())
    hours = uptime_seconds // 3600
    minutes = (uptime_seconds % 3600) // 60

    python_version = platform.python_version()
    system_name = platform.system()

    text = "💻 <b>Система</b>\n━━━━━━━━━━━━━━\n"
    text = text + "🖥 CPU: <b>" + str(cpu) + "%</b>\n"
    text = text + "🧠 RAM: <b>" + str(ram) + "%</b>\n"
    text = text + "💾 Диск: <b>" + str(disk) + "%</b>\n"
    text = text + "⏱ Аптайм: <b>" + str(hours) + "ч " + str(minutes) + "м</b>\n"
    text = text + "🐍 Python: <b>" + python_version + "</b>\n"
    text = text + "📦 ОС: <b>" + system_name + "</b>"

    await callback.message.edit_text(
        text, reply_markup=keyboards.admin_back_keyboard("admin:settings")
    )
    await callback.answer()


@router.callback_query(F.data == "admin:backup_menu")
async def cb_admin_backup_menu(callback: CallbackQuery):
    """Показывает меню бэкапа."""
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    await callback.message.edit_text(
        "🗄 <b>Бэкап / восстановление</b>\n━━━━━━━━━━━━━━\n"
        "📦 Создать — снимет консистентную копию базы и пришлёт zip.\n"
        "♻️ Восстановить — заменит базу содержимым присланного файла.",
        reply_markup=keyboards.admin_backup_keyboard(),
    )
    await callback.answer()


@router.message(Command("backup"))
async def cmd_backup(message: Message, bot: Bot):
    """Делает бэкап сейчас (то же, что ночная задача)."""
    if not is_admin(message.from_user.id):
        return
    await message.answer("📦 Создаю бэкап…")
    await perform_backup(bot)


async def _stage_and_confirm_restore(chat: Message, bot: Bot, doc) -> None:
    """Скачивает бэкап, распаковывает zip в .db и просит подтвердить восстановление.

    Общий путь для команды /restore (ответ на файл) и загрузки через панель.
    """
    os.makedirs("cache/backup", exist_ok=True)
    upload = "cache/backup/restore_upload.bin"
    try:
        await bot.download(doc, destination=upload)
        file_name = doc.file_name or ""
        # Приводим загрузку к сырому .db (распаковываем, если это архив).
        if file_name.lower().endswith(".zip") or zipfile.is_zipfile(upload):
            with zipfile.ZipFile(upload) as zf:
                db_names = [n for n in zf.namelist() if n.endswith(".db")]
                if len(db_names) == 0:
                    await chat.answer("❌ В архиве нет файла .db.")
                    return
                with zf.open(db_names[0]) as src, open(RESTORE_READY, "wb") as out:
                    shutil.copyfileobj(src, out)
        else:
            shutil.copy(upload, RESTORE_READY)
    except Exception as error:
        await chat.answer("❌ Не удалось прочитать файл: " + str(error))
        return

    await chat.answer(
        "⚠️ <b>Восстановление базы</b>\n━━━━━━━━━━━━━━\n"
        "Текущие данные будут <b>полностью заменены</b> содержимым этого файла. "
        "Действие необратимо. Продолжить?",
        reply_markup=keyboards.admin_restore_confirm_keyboard(),
    )


@router.message(Command("restore"))
async def cmd_restore(message: Message, bot: Bot):
    """Восстанавливает базу из бэкапа (ответить командой на файл .zip или .db)."""
    if not is_admin(message.from_user.id):
        return
    doc = None
    if message.reply_to_message is not None:
        doc = message.reply_to_message.document
    if doc is None:
        await message.answer(
            "Чтобы восстановить базу, <b>ответь этой командой на файл бэкапа</b> "
            "(jpn_backup.zip или .db) — напиши <code>/restore</code> в ответ на "
            "сообщение с файлом."
        )
        return
    await _stage_and_confirm_restore(message, bot, doc)


@router.callback_query(F.data == "admin:backup_now")
async def cb_admin_backup_now(callback: CallbackQuery, bot: Bot):
    """Делает бэкап сейчас и присылает его админу."""
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    await callback.answer("Готовлю бэкап…")
    await perform_backup(bot)


@router.callback_query(F.data == "admin:restore_start")
async def cb_admin_restore_start(callback: CallbackQuery, state: FSMContext):
    """Просит прислать файл бэкапа для восстановления."""
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    await state.set_state(AdminStates.waiting_restore_file)
    await callback.message.answer(
        "♻️ Пришли <b>файл бэкапа</b> (jpn_backup.zip или .db) следующим "
        "сообщением.\nЧтобы отменить — /admin."
    )
    await callback.answer()


@router.message(AdminStates.waiting_restore_file, F.document)
async def process_restore_file(message: Message, state: FSMContext, bot: Bot):
    """Скачивает присланный файл и просит подтвердить восстановление."""
    if not is_admin(message.from_user.id):
        await state.clear()
        return
    await state.clear()
    await _stage_and_confirm_restore(message, bot, message.document)


@router.callback_query(F.data == "admin:restore_confirm")
async def cb_admin_restore_confirm(callback: CallbackQuery):
    """Заменяет базу присланным файлом через online backup API."""
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return

    if not os.path.exists(RESTORE_READY):
        await callback.message.edit_text(
            "❌ Файл для восстановления не найден — начни заново."
        )
        await callback.answer()
        return

    try:
        await database.restore_from(RESTORE_READY)
    except Exception as error:
        await callback.message.edit_text(
            "❌ Восстановление не удалось: " + str(error)
        )
        await callback.answer()
        return

    try:
        os.remove(RESTORE_READY)
    except OSError:
        pass

    count = await database.count_users()
    await callback.message.edit_text(
        "✅ База восстановлена. Пользователей в базе: <b>" + str(count) + "</b>."
    )
    await callback.answer()


@router.callback_query(F.data == "admin:restore_cancel")
async def cb_admin_restore_cancel(callback: CallbackQuery):
    """Отменяет восстановление и убирает временный файл."""
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    if os.path.exists(RESTORE_READY):
        try:
            os.remove(RESTORE_READY)
        except OSError:
            pass
    await callback.message.edit_text("Восстановление отменено.")
    await callback.answer()


# ---------------------------------------------------------------------------
# Рассылка (доступна и командой /broadcast, и кнопкой в панели)
# ---------------------------------------------------------------------------


@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message, state: FSMContext):
    """Запускает создание рассылки командой."""
    user_id = message.from_user.id
    lang = await resolve_lang(user_id)

    if not is_admin(user_id):
        await message.answer(get_text(lang, "adm_only"))
        return

    await state.set_state(AdminStates.waiting_broadcast)
    await message.answer(get_text(lang, "adm_bc_enter"))


@router.callback_query(F.data == "admin:broadcast")
async def cb_admin_broadcast(callback: CallbackQuery, state: FSMContext):
    """Запускает создание рассылки из панели."""
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
    lang = await resolve_lang(callback.from_user.id)
    await state.set_state(AdminStates.waiting_broadcast)
    await callback.message.answer(get_text(lang, "adm_bc_enter"))
    await callback.answer()


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
    if not is_admin(callback.from_user.id):
        await callback.answer()
        return
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
