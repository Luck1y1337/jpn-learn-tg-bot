from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message

import database
from common import is_admin


class BlockMiddleware(BaseMiddleware):
    """Не пропускает обновления от заблокированных пользователей.

    Вешается и на сообщения, и на callback-запросы. Администраторы
    проходят всегда, даже если каким-то образом помечены заблокированными.
    """

    async def __call__(self, handler, event, data):
        user = getattr(event, "from_user", None)
        if user is None:
            return await handler(event, data)

        user_id = user.id
        if is_admin(user_id):
            return await handler(event, data)

        blocked = await database.is_user_blocked(user_id)
        if blocked:
            if isinstance(event, CallbackQuery):
                await event.answer("🚫 Вы заблокированы.", show_alert=True)
            elif isinstance(event, Message):
                try:
                    await event.answer("🚫 Вы заблокированы администратором.")
                except Exception:
                    pass
            return

        return await handler(event, data)
