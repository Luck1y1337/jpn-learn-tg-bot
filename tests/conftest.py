import os
import sys

import pytest_asyncio

# Позволяем импортировать модули проекта из каталога выше tests/.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import database  # noqa: E402


@pytest_asyncio.fixture
async def db(tmp_path, monkeypatch):
    """Свежая инициализированная БД на временном файле для каждого теста.

    Все функции database используют модульный DB_PATH, поэтому достаточно
    подменить его — живая база бота (bot.db) не затрагивается.
    """
    path = tmp_path / "test.db"
    monkeypatch.setattr(database, "DB_PATH", str(path))
    await database.init_db()
    yield database
