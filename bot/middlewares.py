from __future__ import annotations

from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from bot.texts import MSG_FORBIDDEN


class AccessMiddleware(BaseMiddleware):
    def __init__(self, allowed_user_ids: frozenset[int]):
        self.allowed_user_ids = allowed_user_ids

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if user is None:
            return None

        if user.id not in self.allowed_user_ids:
            if isinstance(event, Message):
                await event.answer(MSG_FORBIDDEN)
            elif isinstance(event, CallbackQuery):
                await event.answer(MSG_FORBIDDEN, show_alert=True)
            return None

        data["user_id"] = user.id
        return await handler(event, data)
