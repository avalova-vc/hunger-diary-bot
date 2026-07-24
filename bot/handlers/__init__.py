from aiogram import Router

from bot.handlers import export, fallback, hunger, meal, settings, start


def setup_routers() -> Router:
    root = Router()
    root.include_router(start.router)
    root.include_router(hunger.router)
    root.include_router(meal.router)
    root.include_router(export.router)
    root.include_router(settings.router)
    root.include_router(fallback.router)
    return root
