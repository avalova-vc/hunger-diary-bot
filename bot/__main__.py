from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import load_config
from bot.handlers import setup_routers
from bot.middlewares import AccessMiddleware
from bot.models import create_session_factory
from bot.repositories import Repository
from bot.scheduler import setup_scheduler


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    config = load_config()
    session_factory = create_session_factory(str(config.db_path))
    repo = Repository(session_factory, config.timezone, config.wake_up_time)
    repo.ensure_settings()

    bot = Bot(token=config.bot_token)
    dp = Dispatcher(storage=MemoryStorage())
    dp["repo"] = repo
    dp["config"] = config

    access = AccessMiddleware(config.allowed_user_id)
    dp.message.middleware(access)
    dp.callback_query.middleware(access)

    dp.include_router(setup_routers())

    scheduler = setup_scheduler(bot, repo, config)
    scheduler.start()

    logging.info("Bot started for user_id=%s", config.allowed_user_id)
    try:
        await dp.start_polling(bot)
    finally:
        scheduler.shutdown(wait=False)
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
