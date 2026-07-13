from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from config import JLPT_LEVELS
from locales import get_text


def language_keyboard():
    """Инлайн-клавиатура выбора языка интерфейса."""
    buttons = [
        [
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru"),
            InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang:uz"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang:en"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def level_keyboard():
    """Инлайн-клавиатура выбора уровня JLPT (N5..N1)."""
    row = []
    for level in JLPT_LEVELS:
        row.append(
            InlineKeyboardButton(
                text=level, callback_data="setlevel:" + level
            )
        )
    buttons = [row]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def main_menu_keyboard(lang):
    """Постоянное reply-меню внизу экрана."""
    buttons = [
        [
            KeyboardButton(text=get_text(lang, "btn_study")),
            KeyboardButton(text=get_text(lang, "btn_quiz")),
        ],
        [
            KeyboardButton(text=get_text(lang, "btn_grammar")),
            KeyboardButton(text=get_text(lang, "btn_stats")),
        ],
        [
            KeyboardButton(text=get_text(lang, "btn_settings")),
            KeyboardButton(text=get_text(lang, "btn_donate")),
        ],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def study_show_answer_keyboard(lang, item_id):
    """Кнопка «Показать ответ» на лицевой стороне карточки."""
    buttons = [
        [
            InlineKeyboardButton(
                text=get_text(lang, "btn_show_answer"),
                callback_data="study:show:" + str(item_id),
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def study_rating_keyboard(lang, item_id):
    """Кнопки оценки запоминания карточки."""
    buttons = [
        [
            InlineKeyboardButton(
                text=get_text(lang, "rating_again"),
                callback_data="study:rate:" + str(item_id) + ":again",
            ),
            InlineKeyboardButton(
                text=get_text(lang, "rating_hard"),
                callback_data="study:rate:" + str(item_id) + ":hard",
            ),
            InlineKeyboardButton(
                text=get_text(lang, "rating_easy"),
                callback_data="study:rate:" + str(item_id) + ":easy",
            ),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def quiz_options_keyboard(options):
    """Кнопки вариантов ответа квиза. options — список строк."""
    buttons = []
    index = 0
    while index < len(options):
        text = options[index]
        buttons.append(
            [
                InlineKeyboardButton(
                    text=text,
                    callback_data="quiz:ans:" + str(index),
                )
            ]
        )
        index = index + 1
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def grammar_nav_keyboard(lang, index, total):
    """Навигация по грамматическим карточкам (назад/вперёд)."""
    nav_row = []
    if index > 0:
        nav_row.append(
            InlineKeyboardButton(
                text=get_text(lang, "btn_prev"),
                callback_data="grammar:nav:" + str(index - 1),
            )
        )
    nav_row.append(
        InlineKeyboardButton(
            text=str(index + 1) + "/" + str(total),
            callback_data="grammar:noop",
        )
    )
    if index < total - 1:
        nav_row.append(
            InlineKeyboardButton(
                text=get_text(lang, "btn_next"),
                callback_data="grammar:nav:" + str(index + 1),
            )
        )
    buttons = [nav_row]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def settings_keyboard(lang):
    """Меню настроек."""
    buttons = [
        [
            InlineKeyboardButton(
                text=get_text(lang, "btn_set_language"),
                callback_data="settings:lang",
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text(lang, "btn_set_level"),
                callback_data="settings:level",
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text(lang, "btn_set_time"),
                callback_data="settings:time",
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text(lang, "btn_set_count"),
                callback_data="settings:count",
            )
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def amounts_keyboard(lang):
    """Инлайн-клавиатура выбора суммы доната."""
    buttons = [
        [
            InlineKeyboardButton(text="15⭐️", callback_data="donate:amt:15"),
            InlineKeyboardButton(text="50⭐️", callback_data="donate:amt:50"),
            InlineKeyboardButton(text="100⭐️", callback_data="donate:amt:100"),
        ],
        [
            InlineKeyboardButton(text="250⭐️", callback_data="donate:amt:250"),
            InlineKeyboardButton(text="500⭐️", callback_data="donate:amt:500"),
        ],
        [
            InlineKeyboardButton(
                text=get_text(lang, "btn_custom_amount"),
                callback_data="donate:custom",
            )
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def comment_keyboard(lang):
    """Клавиатура шага с комментарием к донату."""
    buttons = [
        [
            InlineKeyboardButton(
                text=get_text(lang, "btn_write_comment"),
                callback_data="comment:write",
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text(lang, "btn_skip"),
                callback_data="comment:skip",
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text(lang, "btn_back"),
                callback_data="donate:open",
            )
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def back_to_amounts_keyboard(lang):
    """Кнопка «Назад» на шаге ввода своей суммы."""
    buttons = [
        [
            InlineKeyboardButton(
                text=get_text(lang, "btn_back"),
                callback_data="donate:open",
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def broadcast_confirm_keyboard(lang):
    """Подтверждение админской рассылки."""
    buttons = [
        [
            InlineKeyboardButton(
                text=get_text(lang, "adm_btn_bc_send"),
                callback_data="admin:bc:send",
            ),
            InlineKeyboardButton(
                text=get_text(lang, "adm_btn_bc_cancel"),
                callback_data="admin:bc:cancel",
            ),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
