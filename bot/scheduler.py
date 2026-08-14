from __future__ import annotations

import logging

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from bot.config import Config
from bot.keyboards import scale_keyboard
from bot.repositories import Repository
from bot.services.reminders import decide_inactivity, should_send_morning
from bot.texts import MSG_INACTIVITY_1, MSG_INACTIVITY_2, MSG_MORNING

logger = logging.getLogger(__name__)


def setup_scheduler(bot: Bot, repo: Repository, config: Config) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone=config.timezone)

    async def morning_job() -> None:
        for user in config.users.values():
            if not should_send_morning(
                repo,
                user.user_id,
                default_wake_up=user.wake_up_time,
            ):
                continue
            await bot.send_message(
                user.user_id,
                MSG_MORNING,
                reply_markup=scale_keyboard("hunger", with_cancel=False),
            )
            repo.log_reminder(user.user_id, "morning")
            logger.info("Sent morning reminder to user_id=%s", user.user_id)

    async def inactivity_job() -> None:
        for user in config.users.values():
            decision = decide_inactivity(
                repo,
                user.user_id,
                config.sleep_time,
                user.inactivity_hours,
                default_wake_up=user.wake_up_time,
            )
            if decision.kind is None:
                continue

            text = MSG_INACTIVITY_1 if decision.kind == "inactivity_1" else MSG_INACTIVITY_2
            await bot.send_message(
                user.user_id,
                text,
                reply_markup=scale_keyboard("hunger", with_cancel=False),
            )
            repo.log_reminder(user.user_id, decision.kind)
            logger.info("Sent %s reminder to user_id=%s", decision.kind, user.user_id)

    scheduler.add_job(morning_job, CronTrigger(minute="*", timezone=config.timezone))
    scheduler.add_job(inactivity_job, IntervalTrigger(minutes=15))
    return scheduler
