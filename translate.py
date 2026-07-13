import asyncio
import logging

from deep_translator import GoogleTranslator

logger = logging.getLogger(__name__)


def _translate_sync(text, target_lang):
    """Синхронный перевод одной строки с английского. Блокирующий вызов."""
    if text is None:
        return ""
    if text == "":
        return ""
    try:
        translator = GoogleTranslator(source="en", target=target_lang)
        result = translator.translate(text)
        if result is None:
            return text
        return result
    except Exception as error:
        logger.warning("Ошибка перевода на %s: %s", target_lang, error)
        return text


async def translate_text(text, target_lang):
    """Асинхронная обёртка над переводом: не блокирует event loop.

    deep-translator работает через обычные HTTP-запросы (блокирующие),
    поэтому запускаем его в отдельном потоке.
    """
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, _translate_sync, text,
                                        target_lang)
    return result


async def translate_to_ru_uz(english_text):
    """Переводит английский текст на русский и узбекский.

    Возвращает кортеж (текст_ru, текст_uz). При ошибке возвращает
    английский текст как запасной вариант (обрабатывается внутри).
    """
    russian = await translate_text(english_text, "ru")
    uzbek = await translate_text(english_text, "uz")
    return russian, uzbek
