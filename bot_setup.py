import logging

from aiogram import Bot
from aiogram.types import (
    BotCommand,
    BotCommandScopeChat,
    BotCommandScopeDefault,
    MenuButtonCommands,
)

from config import ADMIN_IDS
from locales import get_text

logger = logging.getLogger(__name__)

LANGS = ("ru", "en", "uz")

# Публичные команды: (команда, {язык: описание}). Показываются в меню команд.
PUBLIC_COMMANDS = [
    ("start", {"ru": "Начать / выбрать язык", "en": "Start / choose language",
               "uz": "Boshlash / til tanlash"}),
    ("menu", {"ru": "Открыть меню", "en": "Open the menu",
              "uz": "Menyuni ochish"}),
    ("study", {"ru": "Повторение по SRS", "en": "SRS review",
               "uz": "SRS takrori"}),
    ("quiz", {"ru": "Квиз по словам", "en": "Vocabulary quiz",
              "uz": "So'z kvizi"}),
    ("grammar", {"ru": "Грамматика уровня", "en": "Grammar for your level",
                 "uz": "Daraja grammatikasi"}),
    ("stats", {"ru": "Твой прогресс", "en": "Your progress",
               "uz": "Progressingiz"}),
    ("settings", {"ru": "Настройки", "en": "Settings",
                  "uz": "Sozlamalar"}),
    ("donate", {"ru": "Поддержать проект", "en": "Support the project",
                "uz": "Loyihani qo'llab-quvvatlash"}),
    ("language", {"ru": "Сменить язык", "en": "Change language",
                  "uz": "Tilni o'zgartirish"}),
]

# Дополнительные команды только для админов.
ADMIN_EXTRA_COMMANDS = [
    ("admin", {"ru": "Админ-панель", "en": "Admin panel",
               "uz": "Admin panel"}),
    ("broadcast", {"ru": "Рассылка всем", "en": "Broadcast to all",
                   "uz": "Ommaviy xabar"}),
    ("backup", {"ru": "Бэкап базы сейчас", "en": "Backup the DB now",
                "uz": "Bazani zaxiralash"}),
    ("restore", {"ru": "Восстановить базу из файла",
                 "en": "Restore the DB from a file",
                 "uz": "Bazani fayldan tiklash"}),
]


def _commands(defs, lang):
    """Строит список BotCommand для языка (с запасным ru)."""
    result = []
    for command, descriptions in defs:
        description = descriptions.get(lang, descriptions["ru"])
        result.append(BotCommand(command=command, description=description))
    return result


async def setup_bot_profile(bot: Bot):
    """Регистрирует команды-подсказки, описания и кнопку меню.

    Всё обёрнуто в try/except: сбой Bot API не должен мешать запуску polling.
    """
    # Публичные подсказки команд: по языкам + запасной набор без кода языка.
    for lang in LANGS:
        try:
            await bot.set_my_commands(
                _commands(PUBLIC_COMMANDS, lang),
                scope=BotCommandScopeDefault(),
                language_code=lang,
            )
        except Exception as error:
            logger.warning("set_my_commands(%s) не удалось: %s", lang, error)
    try:
        await bot.set_my_commands(
            _commands(PUBLIC_COMMANDS, "ru"), scope=BotCommandScopeDefault()
        )
    except Exception as error:
        logger.warning("set_my_commands(default) не удалось: %s", error)

    # Админские подсказки: на чат каждого админа, по языкам + запасной.
    admin_defs = PUBLIC_COMMANDS + ADMIN_EXTRA_COMMANDS
    for admin_id in ADMIN_IDS:
        for lang in LANGS:
            try:
                await bot.set_my_commands(
                    _commands(admin_defs, lang),
                    scope=BotCommandScopeChat(chat_id=admin_id),
                    language_code=lang,
                )
            except Exception as error:
                logger.warning(
                    "admin set_my_commands(%s, %s) не удалось: %s",
                    admin_id, lang, error,
                )
        try:
            await bot.set_my_commands(
                _commands(admin_defs, "ru"),
                scope=BotCommandScopeChat(chat_id=admin_id),
            )
        except Exception as error:
            logger.warning(
                "admin set_my_commands(%s, default) не удалось: %s",
                admin_id, error,
            )

    # Многоязычное описание бота (видно до /start) и короткое описание (bio).
    for lang in LANGS:
        try:
            await bot.set_my_description(
                get_text(lang, "bot_description"), language_code=lang
            )
            await bot.set_my_short_description(
                get_text(lang, "bot_short_description"), language_code=lang
            )
        except Exception as error:
            logger.warning("set_my_description(%s) не удалось: %s", lang, error)

    # Синяя кнопка «Меню» показывает список команд.
    try:
        await bot.set_chat_menu_button(menu_button=MenuButtonCommands())
    except Exception as error:
        logger.warning("set_chat_menu_button не удалось: %s", error)
