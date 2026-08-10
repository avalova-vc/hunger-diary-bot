from __future__ import annotations

import asyncio
import logging
import os
import socket
import urllib.request

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import TelegramNetworkError, TelegramUnauthorizedError
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import load_config
from bot.handlers import setup_routers
from bot.middlewares import AccessMiddleware
from bot.models import create_session_factory
from bot.repositories import Repository
from bot.scheduler import setup_scheduler

logger = logging.getLogger(__name__)


def resolve_https_proxy() -> str | None:
    """Proxy from .env (VPS) or system settings (Windows)."""
    for key in ("HTTPS_PROXY", "HTTP_PROXY", "https_proxy", "http_proxy"):
        value = (os.getenv(key) or "").strip()
        if value:
            return value if "://" in value else f"http://{value}"

    proxies = urllib.request.getproxies()
    proxy = proxies.get("https") or proxies.get("http")
    if not proxy:
        return None
    return proxy if "://" in proxy else f"http://{proxy}"


def build_session() -> AiohttpSession:
    proxy = resolve_https_proxy()
    session = AiohttpSession(proxy=proxy) if proxy else AiohttpSession()
    # Prefer IPv4 when connecting directly (no proxy)
    if not proxy:
        session._connector_init["family"] = socket.AF_INET
    if proxy:
        logger.info("Using proxy for Telegram API")
    return session


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    config = load_config()
    session_factory = create_session_factory(str(config.db_path))
    repo = Repository(session_factory, config.timezone, config.wake_up_time)
    repo.ensure_settings()

    bot = Bot(token=config.bot_token, session=build_session())
    dp = Dispatcher(storage=MemoryStorage())
    dp["repo"] = repo
    dp["config"] = config

    access = AccessMiddleware(config.allowed_user_id)
    dp.message.middleware(access)
    dp.callback_query.middleware(access)

    dp.include_router(setup_routers())

    scheduler = setup_scheduler(bot, repo, config)
    scheduler.start()

    logger.info("Bot started for user_id=%s", config.allowed_user_id)
    try:
        while True:
            try:
                await dp.start_polling(bot)
                break
            except TelegramUnauthorizedError:
                logger.error(
                    "Токен бота неверный или отозван. Обновите BOT_TOKEN в .env "
                    "(BotFather → /token или /revoke)."
                )
                raise
            except TelegramNetworkError as exc:
                logger.warning("Сеть Telegram недоступна: %s. Повтор через 15 с…", exc)
                await asyncio.sleep(15)
    finally:
        scheduler.shutdown(wait=False)
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
