import json
import logging
import os

import database

logger = logging.getLogger(__name__)

GRAMMAR_FILE = "grammar_points.json"


async def seed_grammar():
    """Загружает статический набор грамматики из JSON в базу.

    Вызывается при старте бота. Использует upsert, поэтому повторный
    запуск просто обновляет существующие записи, а не дублирует их.
    """
    path = os.path.join(os.path.dirname(__file__), GRAMMAR_FILE)
    if not os.path.exists(path):
        logger.warning("Файл грамматики не найден: %s", path)
        return

    with open(path, "r", encoding="utf-8") as file:
        points = json.load(file)

    count = 0
    for point in points:
        level = point.get("level", "")
        title = point.get("title", "")
        structure = point.get("structure", "")
        explanation_ru = point.get("explanation_ru", "")
        explanation_en = point.get("explanation_en", "")
        explanation_uz = point.get("explanation_uz", "")
        examples = point.get("examples", [])
        examples_json = json.dumps(examples, ensure_ascii=False)

        await database.upsert_grammar(
            level, title, structure, explanation_ru, explanation_en,
            explanation_uz, examples_json
        )
        count = count + 1

    logger.info("Загружено грамматических конструкций: %s", count)
