import sqlite3

import pytest

import content_api
import database
import srs
import util
from handlers.quiz import build_questions


# ---------------------------------------------------------------------------
# Пользователи
# ---------------------------------------------------------------------------


async def test_add_user_defaults(db):
    await db.add_user(111, "alice")
    user = await db.get_user(111)
    assert user is not None
    assert user["user_id"] == 111
    assert user["username"] == "alice"
    assert user["lang"] is None
    assert user["level"] is None
    assert user["streak"] == 0
    assert user["is_blocked"] == 0


async def test_add_user_updates_username(db):
    await db.add_user(111, "old")
    await db.add_user(111, "new")
    user = await db.get_user(111)
    assert user["username"] == "new"
    assert await db.count_users() == 1


async def test_get_user_missing_returns_none(db):
    assert await db.get_user(999) is None


async def test_lang_and_level_roundtrip(db):
    await db.add_user(111, "alice")
    await db.set_user_lang(111, "uz")
    await db.set_user_level(111, "N3")
    assert await db.get_user_lang(111) == "uz"
    assert await db.get_user_level(111) == "N3"


async def test_daily_settings(db):
    await db.add_user(111, "alice")
    await db.set_daily_time(111, "07:30")
    await db.set_daily_count(111, 12)
    user = await db.get_user(111)
    assert user["daily_time"] == "07:30"
    assert user["daily_count"] == 12


async def test_streak(db):
    await db.add_user(111, "alice")
    await db.set_streak(111, 5, "2026-07-18")
    user = await db.get_user(111)
    assert user["streak"] == 5
    assert user["last_study_date"] == "2026-07-18"


async def test_block_flow(db):
    await db.add_user(111, "alice")
    assert await db.is_user_blocked(111) is False
    await db.set_user_blocked(111, 1)
    assert await db.is_user_blocked(111) is True
    assert await db.count_blocked_users() == 1
    await db.set_user_blocked(111, 0)
    assert await db.is_user_blocked(111) is False


async def test_is_user_blocked_missing(db):
    assert await db.is_user_blocked(404) is False


async def test_find_users(db):
    await db.add_user(111, "alice")
    await db.add_user(222, "bob")
    by_id = await db.find_users("111")
    assert len(by_id) == 1 and by_id[0]["user_id"] == 111
    by_name = await db.find_users("@ali")
    assert len(by_name) == 1 and by_name[0]["username"] == "alice"


async def test_users_page_and_ids(db):
    await db.add_user(111, "alice")
    await db.add_user(222, "bob")
    page = await db.get_users_page(0, 10)
    assert len(page) == 2
    ids = await db.get_all_user_ids()
    assert set(ids) == {111, 222}


async def test_user_distributions(db):
    await db.add_user(111, "alice")
    await db.add_user(222, "bob")
    await db.set_user_level(111, "N5")
    await db.set_user_level(222, "N5")
    await db.set_user_lang(111, "ru")
    by_level = await db.count_users_by_level()
    by_lang = await db.count_users_by_lang()
    assert by_level.get("N5") == 2
    assert by_lang.get("ru") == 1


# ---------------------------------------------------------------------------
# SRS-прогресс
# ---------------------------------------------------------------------------


async def test_srs_add_and_due(db):
    await db.add_user(111, "alice")
    today = util.today_str()
    await db.add_srs_item(
        111, "word", "水", "水", "みず", "вода", "water", "suv", today
    )
    assert await db.has_srs_item(111, "word", "水") is True
    due = await db.get_due_items(111, today, 10)
    assert len(due) == 1
    assert await db.count_due_items(111, today) == 1
    assert await db.count_total_srs(111) == 1
    assert await db.count_learned(111) == 0


async def test_srs_add_is_idempotent(db):
    await db.add_user(111, "alice")
    today = util.today_str()
    for _ in range(2):
        await db.add_srs_item(
            111, "word", "水", "水", "みず", "вода", "water", "suv", today
        )
    assert await db.count_total_srs(111) == 1


async def test_srs_update_marks_learned(db):
    await db.add_user(111, "alice")
    today = util.today_str()
    await db.add_srs_item(
        111, "word", "水", "水", "みず", "вода", "water", "suv", today
    )
    due = await db.get_due_items(111, today, 1)
    item_id = due[0]["id"]
    await db.update_srs_item(item_id, 6, 2.5, 1, "2099-01-01")
    assert await db.count_learned(111) == 1
    # Уже не должно быть к повторению сегодня.
    assert await db.count_due_items(111, today) == 0
    stored = await db.get_srs_item(item_id)
    assert stored["repetitions"] == 1
    assert stored["interval"] == 6


# ---------------------------------------------------------------------------
# Квизы, кэш, грамматика
# ---------------------------------------------------------------------------


async def test_quiz_results(db):
    await db.add_user(111, "alice")
    await db.add_quiz_result(111, 4, 5)
    await db.add_quiz_result(111, 3, 5)
    count, correct, total = await db.get_quiz_stats(111)
    assert count == 2
    assert correct == 7
    assert total == 10
    assert await db.count_all_quizzes() == 2


async def test_word_cache(db):
    await db.upsert_word("水", "N5", "みず", "mizu", "water", "вода", "suv")
    row = await db.get_word("水")
    assert row["meaning_ru"] == "вода"
    assert await db.count_cached_words("N5") == 1
    assert await db.count_all_cached_words() == 1
    randoms = await db.get_random_cached_words("N5", 5)
    assert len(randoms) == 1


async def test_kanji_cache(db):
    await db.upsert_kanji(
        "水", "N5", "water", "вода", "suv", "みず", "スイ", 4
    )
    row = await db.get_kanji("水")
    assert row["meaning_en"] == "water"
    assert row["stroke_count"] == 4
    assert await db.count_all_cached_kanji() == 1


async def test_grammar(db):
    await db.upsert_grammar(
        "N5", "は", "N は", "тема", "topic", "mavzu", "[]"
    )
    rows = await db.get_grammar_by_level("N5")
    assert len(rows) == 1
    assert rows[0]["title"] == "は"
    assert await db.count_grammar_by_level("N5") == 1
    assert await db.count_all_grammar() == 1
    one = await db.get_random_grammar("N5")
    assert one is not None


async def test_donations_summary(db):
    await db.add_user(111, "alice")
    await db.add_donation(111, "alice", 50, "спасибо", "charge_1")
    count, total = await db.get_donations_summary()
    assert count == 1
    assert total == 50
    assert await db.get_user_donation_total(111) == 50


# ---------------------------------------------------------------------------
# Бэкап / восстановление
# ---------------------------------------------------------------------------


async def test_backup_and_restore(db, tmp_path):
    await db.add_user(111, "alice")
    snapshot = str(tmp_path / "snap.db")
    await db.backup_to(snapshot)

    # Мутация после снимка — restore должен её откатить.
    await db.add_user(222, "bob")
    assert await db.count_users() == 2

    await db.restore_from(snapshot)
    assert await db.count_users() == 1


async def test_restore_rejects_foreign_db(db, tmp_path):
    bogus = str(tmp_path / "bogus.db")
    conn = sqlite3.connect(bogus)
    conn.execute("CREATE TABLE junk (x)")
    conn.commit()
    conn.close()
    with pytest.raises(ValueError):
        await db.restore_from(bogus)


# ---------------------------------------------------------------------------
# Алгоритм SM-2 (srs.py) — чистые функции, без БД
# ---------------------------------------------------------------------------


def test_srs_again_resets():
    reps, interval, ease, due = srs.review("again", 5, 30, 2.5)
    assert reps == 0
    assert interval == 1
    assert isinstance(due, str)


def test_srs_easy_progression():
    reps, interval, ease, _ = srs.review("easy", 0, 0, 2.5)
    assert (reps, interval) == (1, 1)
    reps, interval, ease, _ = srs.review("easy", 1, 1, 2.5)
    assert (reps, interval) == (2, 6)
    reps, interval, ease, _ = srs.review("easy", 2, 6, 2.5)
    assert reps == 3
    assert interval == round(6 * 2.5)


def test_srs_ease_floor():
    # Многократные «again» не должны опускать ease ниже 1.3.
    ease = 1.3
    for _ in range(5):
        _, _, ease, _ = srs.review("again", 0, 1, ease)
    assert ease >= srs.MIN_EASE


def test_srs_new_item_due_is_today():
    assert srs.new_item_due_date() == util.today_str()


# ---------------------------------------------------------------------------
# Утилиты дат/времени (util.py)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "value,expected",
    [
        ("09:00", True),
        ("23:59", True),
        ("00:00", True),
        ("24:00", False),
        ("09:60", False),
        ("9-00", False),
        ("abc", False),
        ("", False),
        (None, False),
    ],
)
def test_is_valid_time(value, expected):
    assert util.is_valid_time(value) is expected


def test_normalize_time_pads():
    assert util.normalize_time("9:5") == "09:05"
    assert util.normalize_time("07:30") == "07:30"


def test_days_between():
    assert util.days_between("2026-07-17", "2026-07-18") == 1
    assert util.days_between("2026-07-18", "2026-07-18") == 0
    assert util.days_between("2026-07-18", "2026-07-17") == -1


# ---------------------------------------------------------------------------
# content_api / quiz — чистая логика
# ---------------------------------------------------------------------------


def test_level_to_number():
    assert content_api.level_to_number("N5") == 5
    assert content_api.level_to_number("N1") == 1
    assert content_api.level_to_number("bad") == 5


def test_build_questions_correct_index():
    pool = [
        {"word": "一", "meaning_ru": "один", "meaning_en": "one",
         "meaning_uz": "bir"},
        {"word": "二", "meaning_ru": "два", "meaning_en": "two",
         "meaning_uz": "ikki"},
        {"word": "三", "meaning_ru": "три", "meaning_en": "three",
         "meaning_uz": "uch"},
        {"word": "四", "meaning_ru": "четыре", "meaning_en": "four",
         "meaning_uz": "tort"},
        {"word": "五", "meaning_ru": "пять", "meaning_en": "five",
         "meaning_uz": "besh"},
    ]
    questions = build_questions("ru", pool)
    assert len(questions) == len(pool)
    for q, source in zip(questions, pool):
        # Правильный вариант действительно лежит по correct_index.
        assert q["options"][q["correct_index"]] == source["meaning_ru"]
        assert len(q["options"]) <= 4
        assert len(q["options"]) == len(set(q["options"]))
