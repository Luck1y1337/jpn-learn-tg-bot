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
    """Постоянная reply-кнопка-лаунчер «☰ Меню», открывающая инлайн-хаб."""
    buttons = [[KeyboardButton(text=get_text(lang, "btn_menu"))]]
    return ReplyKeyboardMarkup(
        keyboard=buttons, resize_keyboard=True, is_persistent=True
    )


def main_hub_keyboard(lang, is_admin=False):
    """Инлайн-хаб со всеми разделами бота (все команды — кнопками)."""
    buttons = [
        [
            InlineKeyboardButton(
                text=get_text(lang, "btn_study"), callback_data="menu:study"
            ),
            InlineKeyboardButton(
                text=get_text(lang, "btn_quiz"), callback_data="menu:quiz"
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_text(lang, "btn_grammar"),
                callback_data="menu:grammar",
            ),
            InlineKeyboardButton(
                text=get_text(lang, "btn_stats"), callback_data="menu:stats"
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_text(lang, "btn_settings"),
                callback_data="menu:settings",
            ),
            InlineKeyboardButton(
                text=get_text(lang, "btn_donate"), callback_data="menu:donate"
            ),
        ],
        [
            InlineKeyboardButton(
                text=get_text(lang, "btn_set_language"),
                callback_data="menu:language",
            ),
        ],
    ]
    if is_admin:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="👑 Админ-панель", callback_data="menu:admin"
                )
            ]
        )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


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


# ---------------------------------------------------------------------------
# Админ-панель (интерфейс только на русском — для владельца бота)
# ---------------------------------------------------------------------------


def admin_main_keyboard():
    """Главное меню админ-панели."""
    buttons = [
        [
            InlineKeyboardButton(
                text="📊 Статистика", callback_data="admin:stats"
            ),
            InlineKeyboardButton(
                text="👥 Пользователи", callback_data="admin:users:0"
            ),
        ],
        [
            InlineKeyboardButton(
                text="📢 Рассылка", callback_data="admin:broadcast"
            ),
            InlineKeyboardButton(
                text="🔨 Бан / разбан", callback_data="admin:ban_menu"
            ),
        ],
        [
            InlineKeyboardButton(
                text="⚙️ Настройки", callback_data="admin:settings"
            ),
        ],
        [
            InlineKeyboardButton(
                text="✖️ Закрыть", callback_data="admin:close"
            ),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_back_keyboard(target):
    """Кнопка «Назад» для админ-панели с указанием, куда возвращаться."""
    buttons = [
        [InlineKeyboardButton(text="« Назад", callback_data=target)]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_ban_menu_keyboard():
    """Меню блокировки пользователей."""
    buttons = [
        [
            InlineKeyboardButton(
                text="🔨 Забанить", callback_data="admin:ban"
            ),
            InlineKeyboardButton(
                text="♻️ Разбанить", callback_data="admin:unban"
            ),
        ],
        [InlineKeyboardButton(text="« Назад", callback_data="admin:main")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_settings_keyboard():
    """Меню настроек админ-панели."""
    buttons = [
        [
            InlineKeyboardButton(
                text="💻 Система", callback_data="admin:sysinfo"
            ),
        ],
        [
            InlineKeyboardButton(
                text="🗄 Бэкап / восстановление",
                callback_data="admin:backup_menu",
            ),
        ],
        [InlineKeyboardButton(text="« Назад", callback_data="admin:main")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_backup_keyboard():
    """Меню бэкапа и восстановления базы."""
    buttons = [
        [
            InlineKeyboardButton(
                text="📦 Создать бэкап", callback_data="admin:backup_now"
            ),
        ],
        [
            InlineKeyboardButton(
                text="♻️ Восстановить", callback_data="admin:restore_start"
            ),
        ],
        [InlineKeyboardButton(text="« Назад", callback_data="admin:settings")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_restore_confirm_keyboard():
    """Подтверждение восстановления базы из файла."""
    buttons = [
        [
            InlineKeyboardButton(
                text="✅ Да, восстановить",
                callback_data="admin:restore_confirm",
            ),
            InlineKeyboardButton(
                text="❌ Отмена", callback_data="admin:restore_cancel"
            ),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_users_keyboard(offset, page_size, has_next):
    """Навигация по списку пользователей + поиск и возврат."""
    nav_row = []
    if offset > 0:
        prev_offset = offset - page_size
        if prev_offset < 0:
            prev_offset = 0
        nav_row.append(
            InlineKeyboardButton(
                text="⬅️", callback_data="admin:users:" + str(prev_offset)
            )
        )
    if has_next:
        next_offset = offset + page_size
        nav_row.append(
            InlineKeyboardButton(
                text="➡️", callback_data="admin:users:" + str(next_offset)
            )
        )

    buttons = []
    if len(nav_row) > 0:
        buttons.append(nav_row)
    buttons.append(
        [
            InlineKeyboardButton(
                text="🔍 Поиск", callback_data="admin:users_search"
            )
        ]
    )
    buttons.append(
        [InlineKeyboardButton(text="« Назад", callback_data="admin:main")]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)
