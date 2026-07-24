from __future__ import annotations

from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from bot.texts import MSG_FORBIDDEN


class AccessMiddleware(BaseMiddleware):
    def __init__(self, allowed_user_id: int):
        self.allowed_user_id = allowed_user_id

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if user is None:
            return None

        if user.id != self.allowed_user_id:
            if isinstance(event, Message):
                await event.answer(MSG_FORBIDDEN)
            elif isinstance(event, CallbackQuery):
                await event.answer(MSG_FORBIDDEN, show_alert=True)
            return None

        return await handler(event, data)
