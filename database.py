import time

import aiosqlite

from config import (
    DB_PATH,
    DEFAULT_DAILY_COUNT,
    DEFAULT_DAILY_TIME,
)


async def init_db():
    """Создаёт все таблицы бота, если их ещё нет."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "CREATE TABLE IF NOT EXISTS users ("
            "user_id INTEGER PRIMARY KEY, "
            "username TEXT, "
            "lang TEXT, "
            "level TEXT, "
            "daily_time TEXT, "
            "daily_count INTEGER, "
            "last_daily_date TEXT, "
            "streak INTEGER DEFAULT 0, "
            "last_study_date TEXT, "
            "is_blocked INTEGER DEFAULT 0, "
            "created_at INTEGER)"
        )
        try:
            await db.execute(
                "ALTER TABLE users ADD COLUMN is_blocked INTEGER DEFAULT 0"
            )
            await db.commit()
        except Exception:
            pass
        await db.execute(
            "CREATE TABLE IF NOT EXISTS kanji_cache ("
            "character TEXT PRIMARY KEY, "
            "jlpt_level TEXT, "
            "meaning_en TEXT, "
            "meaning_ru TEXT, "
            "meaning_uz TEXT, "
            "kun_readings TEXT, "
            "on_readings TEXT, "
            "stroke_count INTEGER, "
            "updated_at INTEGER)"
        )
        await db.execute(
            "CREATE TABLE IF NOT EXISTS vocab_cache ("
            "word TEXT PRIMARY KEY, "
            "level TEXT, "
            "reading TEXT, "
            "romaji TEXT, "
            "meaning_en TEXT, "
            "meaning_ru TEXT, "
            "meaning_uz TEXT, "
            "updated_at INTEGER)"
        )
        await db.execute(
            "CREATE TABLE IF NOT EXISTS grammar_points ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "level TEXT, "
            "title TEXT, "
            "structure TEXT, "
            "explanation_ru TEXT, "
            "explanation_en TEXT, "
            "explanation_uz TEXT, "
            "examples TEXT, "
            "UNIQUE(level, title))"
        )
        await db.execute(
            "CREATE TABLE IF NOT EXISTS srs_progress ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "user_id INTEGER, "
            "item_type TEXT, "
            "item_key TEXT, "
            "front TEXT, "
            "reading TEXT, "
            "meaning_ru TEXT, "
            "meaning_en TEXT, "
            "meaning_uz TEXT, "
            "interval INTEGER DEFAULT 0, "
            "ease REAL DEFAULT 2.5, "
            "repetitions INTEGER DEFAULT 0, "
            "due_date TEXT, "
            "created_at INTEGER, "
            "updated_at INTEGER, "
            "UNIQUE(user_id, item_type, item_key))"
        )
        await db.execute(
            "CREATE TABLE IF NOT EXISTS quiz_results ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "user_id INTEGER, "
            "correct INTEGER, "
            "total INTEGER, "
            "created_at INTEGER)"
        )
        await db.execute(
            "CREATE TABLE IF NOT EXISTS donations ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "user_id INTEGER, "
            "username TEXT, "
            "amount INTEGER, "
            "message TEXT, "
            "charge_id TEXT, "
            "created_at INTEGER)"
        )
        await db.commit()


# ---------------------------------------------------------------------------
# Пользователи
# ---------------------------------------------------------------------------


async def add_user(user_id, username):
    """Добавляет пользователя со значениями по умолчанию и обновляет username."""
    now = int(time.time())
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users "
            "(user_id, username, lang, level, daily_time, daily_count, "
            "last_daily_date, streak, last_study_date, created_at) "
            "VALUES (?, ?, NULL, NULL, ?, ?, NULL, 0, NULL, ?)",
            (user_id, username, DEFAULT_DAILY_TIME, DEFAULT_DAILY_COUNT, now),
        )
        await db.execute(
            "UPDATE users SET username = ? WHERE user_id = ?",
            (username, user_id),
        )
        await db.commit()


async def get_user(user_id):
    """Возвращает строку пользователя или None."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        )
        row = await cursor.fetchone()
        return row


async def get_user_lang(user_id):
    """Возвращает язык интерфейса пользователя или None."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT lang FROM users WHERE user_id = ?", (user_id,)
        )
        row = await cursor.fetchone()
        if row is None:
            return None
        return row[0]


async def set_user_lang(user_id, lang):
    """Сохраняет язык интерфейса пользователя."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET lang = ? WHERE user_id = ?", (lang, user_id)
        )
        await db.commit()


async def get_user_level(user_id):
    """Возвращает уровень JLPT пользователя или None."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT level FROM users WHERE user_id = ?", (user_id,)
        )
        row = await cursor.fetchone()
        if row is None:
            return None
        return row[0]


async def set_user_level(user_id, level):
    """Сохраняет уровень JLPT пользователя."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET level = ? WHERE user_id = ?", (level, user_id)
        )
        await db.commit()


async def set_daily_time(user_id, daily_time):
    """Сохраняет время ежедневной рассылки (HH:MM)."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET daily_time = ? WHERE user_id = ?",
            (daily_time, user_id),
        )
        await db.commit()


async def set_daily_count(user_id, daily_count):
    """Сохраняет количество новых слов в ежедневной рассылке."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET daily_count = ? WHERE user_id = ?",
            (daily_count, user_id),
        )
        await db.commit()


async def set_last_daily_date(user_id, date_str):
    """Запоминает дату последней ежедневной рассылки, чтобы не слать дважды."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET last_daily_date = ? WHERE user_id = ?",
            (date_str, user_id),
        )
        await db.commit()


async def set_streak(user_id, streak, last_study_date):
    """Сохраняет текущий стрик и дату последнего занятия."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET streak = ?, last_study_date = ? "
            "WHERE user_id = ?",
            (streak, last_study_date, user_id),
        )
        await db.commit()


async def get_all_users():
    """Возвращает всех пользователей для планировщика рассылки."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM users")
        rows = await cursor.fetchall()
        return rows


async def count_users():
    """Возвращает количество пользователей бота."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM users")
        row = await cursor.fetchone()
        return row[0]


async def get_all_user_ids():
    """Возвращает список всех user_id для рассылки."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT user_id FROM users")
        rows = await cursor.fetchall()
        result = []
        for row in rows:
            result.append(row[0])
        return result


async def get_users_page(offset, limit):
    """Возвращает страницу пользователей для админ-панели."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM users ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset),
        )
        rows = await cursor.fetchall()
        return rows


async def find_users(query):
    """Ищет пользователей по user_id или части username."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        clean_query = query.lstrip("@")
        if clean_query.isdigit():
            cursor = await db.execute(
                "SELECT * FROM users WHERE user_id = ? LIMIT 20",
                (int(clean_query),),
            )
        else:
            like_value = "%" + clean_query + "%"
            cursor = await db.execute(
                "SELECT * FROM users WHERE username LIKE ? "
                "ORDER BY created_at DESC LIMIT 20",
                (like_value,),
            )
        rows = await cursor.fetchall()
        return rows


async def set_user_blocked(user_id, is_blocked):
    """Устанавливает флаг блокировки пользователя (1 или 0)."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET is_blocked = ? WHERE user_id = ?",
            (is_blocked, user_id),
        )
        await db.commit()


async def is_user_blocked(user_id):
    """Проверяет, заблокирован ли пользователь."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT is_blocked FROM users WHERE user_id = ?", (user_id,)
        )
        row = await cursor.fetchone()
        if row is None:
            return False
        if row[0] == 1:
            return True
        return False


async def count_blocked_users():
    """Возвращает число заблокированных пользователей."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT COUNT(*) FROM users WHERE is_blocked = 1"
        )
        row = await cursor.fetchone()
        return row[0]


async def count_users_by_level():
    """Возвращает распределение пользователей по уровням JLPT."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT level, COUNT(*) FROM users "
            "WHERE level IS NOT NULL GROUP BY level"
        )
        rows = await cursor.fetchall()
        result = {}
        for row in rows:
            result[row[0]] = row[1]
        return result


async def count_users_by_lang():
    """Возвращает распределение пользователей по языкам интерфейса."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT lang, COUNT(*) FROM users "
            "WHERE lang IS NOT NULL GROUP BY lang"
        )
        rows = await cursor.fetchall()
        result = {}
        for row in rows:
            result[row[0]] = row[1]
        return result


async def count_all_srs():
    """Возвращает общее число карточек SRS всех пользователей."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM srs_progress")
        row = await cursor.fetchone()
        return row[0]


async def count_all_quizzes():
    """Возвращает общее число пройденных квизов."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM quiz_results")
        row = await cursor.fetchone()
        return row[0]


async def get_donations_summary():
    """Возвращает (число донатов, сумму звёзд)."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT COUNT(*), COALESCE(SUM(amount), 0) FROM donations"
        )
        row = await cursor.fetchone()
        return row[0], row[1]


async def count_all_cached_words():
    """Возвращает общее число слов в кэше."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM vocab_cache")
        row = await cursor.fetchone()
        return row[0]


async def count_all_cached_kanji():
    """Возвращает общее число кандзи в кэше."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM kanji_cache")
        row = await cursor.fetchone()
        return row[0]


async def count_all_grammar():
    """Возвращает общее число грамматических конструкций."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM grammar_points")
        row = await cursor.fetchone()
        return row[0]


# ---------------------------------------------------------------------------
# Кэш кандзи
# ---------------------------------------------------------------------------


async def upsert_kanji(character, jlpt_level, meaning_en, meaning_ru,
                       meaning_uz, kun_readings, on_readings, stroke_count):
    """Сохраняет или обновляет кандзи в локальном кэше."""
    now = int(time.time())
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO kanji_cache "
            "(character, jlpt_level, meaning_en, meaning_ru, meaning_uz, "
            "kun_readings, on_readings, stroke_count, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(character) DO UPDATE SET "
            "jlpt_level = excluded.jlpt_level, "
            "meaning_en = excluded.meaning_en, "
            "meaning_ru = excluded.meaning_ru, "
            "meaning_uz = excluded.meaning_uz, "
            "kun_readings = excluded.kun_readings, "
            "on_readings = excluded.on_readings, "
            "stroke_count = excluded.stroke_count, "
            "updated_at = excluded.updated_at",
            (character, jlpt_level, meaning_en, meaning_ru, meaning_uz,
             kun_readings, on_readings, stroke_count, now),
        )
        await db.commit()


async def get_kanji(character):
    """Возвращает кандзи из кэша или None."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM kanji_cache WHERE character = ?", (character,)
        )
        row = await cursor.fetchone()
        return row


# ---------------------------------------------------------------------------
# Кэш слов
# ---------------------------------------------------------------------------


async def upsert_word(word, level, reading, romaji, meaning_en, meaning_ru,
                      meaning_uz):
    """Сохраняет или обновляет слово в локальном кэше."""
    now = int(time.time())
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO vocab_cache "
            "(word, level, reading, romaji, meaning_en, meaning_ru, "
            "meaning_uz, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(word) DO UPDATE SET "
            "level = excluded.level, "
            "reading = excluded.reading, "
            "romaji = excluded.romaji, "
            "meaning_en = excluded.meaning_en, "
            "meaning_ru = excluded.meaning_ru, "
            "meaning_uz = excluded.meaning_uz, "
            "updated_at = excluded.updated_at",
            (word, level, reading, romaji, meaning_en, meaning_ru,
             meaning_uz, now),
        )
        await db.commit()


async def get_word(word):
    """Возвращает слово из кэша или None."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM vocab_cache WHERE word = ?", (word,)
        )
        row = await cursor.fetchone()
        return row


async def get_random_cached_words(level, limit):
    """Возвращает случайные слова уровня из кэша (для дистракторов квиза)."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM vocab_cache WHERE level = ? "
            "ORDER BY RANDOM() LIMIT ?",
            (level, limit),
        )
        rows = await cursor.fetchall()
        return rows


async def count_cached_words(level):
    """Возвращает число слов уровня в кэше."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT COUNT(*) FROM vocab_cache WHERE level = ?", (level,)
        )
        row = await cursor.fetchone()
        return row[0]


# ---------------------------------------------------------------------------
# Грамматика
# ---------------------------------------------------------------------------


async def upsert_grammar(level, title, structure, explanation_ru,
                         explanation_en, explanation_uz, examples_json):
    """Сохраняет или обновляет грамматическую конструкцию."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO grammar_points "
            "(level, title, structure, explanation_ru, explanation_en, "
            "explanation_uz, examples) "
            "VALUES (?, ?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(level, title) DO UPDATE SET "
            "structure = excluded.structure, "
            "explanation_ru = excluded.explanation_ru, "
            "explanation_en = excluded.explanation_en, "
            "explanation_uz = excluded.explanation_uz, "
            "examples = excluded.examples",
            (level, title, structure, explanation_ru, explanation_en,
             explanation_uz, examples_json),
        )
        await db.commit()


async def get_grammar_by_level(level):
    """Возвращает все грамматические конструкции уровня по порядку."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM grammar_points WHERE level = ? ORDER BY id ASC",
            (level,),
        )
        rows = await cursor.fetchall()
        return rows


async def get_random_grammar(level):
    """Возвращает одну случайную грамматическую конструкцию уровня или None."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM grammar_points WHERE level = ? "
            "ORDER BY RANDOM() LIMIT 1",
            (level,),
        )
        row = await cursor.fetchone()
        return row


async def count_grammar_by_level(level):
    """Возвращает число грамматических конструкций уровня."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT COUNT(*) FROM grammar_points WHERE level = ?", (level,)
        )
        row = await cursor.fetchone()
        return row[0]


# ---------------------------------------------------------------------------
# SRS-прогресс
# ---------------------------------------------------------------------------


async def add_srs_item(user_id, item_type, item_key, front, reading,
                       meaning_ru, meaning_en, meaning_uz, due_date):
    """Добавляет новую карточку в SRS пользователя, если её ещё нет."""
    now = int(time.time())
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO srs_progress "
            "(user_id, item_type, item_key, front, reading, meaning_ru, "
            "meaning_en, meaning_uz, interval, ease, repetitions, due_date, "
            "created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, 2.5, 0, ?, ?, ?)",
            (user_id, item_type, item_key, front, reading, meaning_ru,
             meaning_en, meaning_uz, due_date, now, now),
        )
        await db.commit()


async def has_srs_item(user_id, item_type, item_key):
    """Проверяет, есть ли уже такая карточка у пользователя."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT 1 FROM srs_progress "
            "WHERE user_id = ? AND item_type = ? AND item_key = ?",
            (user_id, item_type, item_key),
        )
        row = await cursor.fetchone()
        if row is None:
            return False
        return True


async def get_due_items(user_id, today_str_value, limit):
    """Возвращает карточки, которые пора повторить (due_date <= сегодня)."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM srs_progress "
            "WHERE user_id = ? AND due_date <= ? "
            "ORDER BY due_date ASC LIMIT ?",
            (user_id, today_str_value, limit),
        )
        rows = await cursor.fetchall()
        return rows


async def get_srs_item(item_id):
    """Возвращает одну карточку по id или None."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM srs_progress WHERE id = ?", (item_id,)
        )
        row = await cursor.fetchone()
        return row


async def update_srs_item(item_id, interval, ease, repetitions, due_date):
    """Обновляет карточку после оценки пользователем."""
    now = int(time.time())
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE srs_progress SET interval = ?, ease = ?, "
            "repetitions = ?, due_date = ?, updated_at = ? WHERE id = ?",
            (interval, ease, repetitions, due_date, now, item_id),
        )
        await db.commit()


async def count_due_items(user_id, today_str_value):
    """Возвращает число карточек, готовых к повторению."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT COUNT(*) FROM srs_progress "
            "WHERE user_id = ? AND due_date <= ?",
            (user_id, today_str_value),
        )
        row = await cursor.fetchone()
        return row[0]


async def count_total_srs(user_id):
    """Возвращает общее число карточек пользователя."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT COUNT(*) FROM srs_progress WHERE user_id = ?", (user_id,)
        )
        row = await cursor.fetchone()
        return row[0]


async def count_learned(user_id):
    """Возвращает число карточек, которые пользователь уже повторял хоть раз."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT COUNT(*) FROM srs_progress "
            "WHERE user_id = ? AND repetitions > 0",
            (user_id,),
        )
        row = await cursor.fetchone()
        return row[0]


# ---------------------------------------------------------------------------
# Результаты квизов
# ---------------------------------------------------------------------------


async def add_quiz_result(user_id, correct, total):
    """Сохраняет результат одного квиза."""
    now = int(time.time())
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO quiz_results (user_id, correct, total, created_at) "
            "VALUES (?, ?, ?, ?)",
            (user_id, correct, total, now),
        )
        await db.commit()


async def get_quiz_stats(user_id):
    """Возвращает (число квизов, сумму верных, сумму вопросов) пользователя."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT COUNT(*), COALESCE(SUM(correct), 0), "
            "COALESCE(SUM(total), 0) FROM quiz_results WHERE user_id = ?",
            (user_id,),
        )
        row = await cursor.fetchone()
        return row[0], row[1], row[2]


# ---------------------------------------------------------------------------
# Донаты
# ---------------------------------------------------------------------------


async def add_donation(user_id, username, amount, message, charge_id):
    """Сохраняет донат и возвращает его id."""
    now = int(time.time())
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO donations "
            "(user_id, username, amount, message, charge_id, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, username, amount, message, charge_id, now),
        )
        await db.commit()
        return cursor.lastrowid


async def get_user_donation_total(user_id):
    """Возвращает суммарный размер донатов пользователя."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM donations WHERE user_id = ?",
            (user_id,),
        )
        row = await cursor.fetchone()
        return row[0]
