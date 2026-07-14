import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

import database
import scheduler
from config import BOT_TOKEN
from middleware import BlockMiddleware
from handlers import (
    admin,
    donate,
    grammar,
    quiz,
    settings,
    start,
    stats,
    study,
)
from seed import seed_grammar


async def main():
    """Точка входа: инициализирует базу, планировщик и запускает polling."""
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stdout,
        format="%(asctime)s %(levelname)s:%(name)s:%(message)s",
    )

    if BOT_TOKEN == "":
        print("Ошибка: BOT_TOKEN не задан. Заполните файл .env.")
        return

    await database.init_db()
    await seed_grammar()

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    block_middleware = BlockMiddleware()
    dp.message.middleware(block_middleware)
    dp.callback_query.middleware(block_middleware)

    dp.include_router(start.router)
    dp.include_router(admin.router)
    dp.include_router(study.router)
    dp.include_router(quiz.router)
    dp.include_router(grammar.router)
    dp.include_router(settings.router)
    dp.include_router(stats.router)
    dp.include_router(donate.router)

    scheduler.start_scheduler(bot)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
