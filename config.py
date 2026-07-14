import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Администраторы. В ADMIN_ID можно указать один ID или несколько через запятую,
# например: ADMIN_ID=111111111,222222222
_admin_raw = os.getenv("ADMIN_ID", "0")
ADMIN_IDS = []
for _part in _admin_raw.split(","):
    _part = _part.strip()
    if _part.isdigit():
        _admin_value = int(_part)
        if _admin_value != 0:
            ADMIN_IDS.append(_admin_value)

if len(ADMIN_IDS) > 0:
    ADMIN_ID = ADMIN_IDS[0]
else:
    ADMIN_ID = 0

DB_PATH = os.getenv("DB_PATH", "bot.db")

# Часовой пояс, в котором считается «сегодня» для стрика и время рассылки.
# Пример значений: "UTC", "Europe/Moscow", "Asia/Tashkent".
TIMEZONE = os.getenv("TIMEZONE", "UTC")

# Уровни JLPT, которые может выбрать пользователь.
JLPT_LEVELS = ["N5", "N4", "N3", "N2", "N1"]

# Языки интерфейса.
LANGS = ["ru", "en", "uz"]
DEFAULT_LANG = "ru"

# Сколько новых слов присылать в ежедневной рассылке по умолчанию.
DEFAULT_DAILY_COUNT = 5
MIN_DAILY_COUNT = 1
MAX_DAILY_COUNT = 20

# Время ежедневной рассылки по умолчанию (в формате HH:MM).
DEFAULT_DAILY_TIME = "09:00"

# Настройки квиза.
QUIZ_QUESTIONS = 5
QUIZ_OPTIONS = 4

# Внешние API с контентом.
KANJI_API_BASE = "https://kanjiapi.dev/v1"
VOCAB_API_BASE = "https://jlpt-vocab-api.vercel.app/api"

# Тайм-аут на один HTTP-запрос к внешнему API (в секундах).
HTTP_TIMEOUT = 15

# Донаты через Telegram Stars.
MIN_DONATE_AMOUNT = 1
MAX_DONATE_AMOUNT = 10000
THANK_YOU_STICKER_ID = os.getenv("THANK_YOU_STICKER_ID", "")
