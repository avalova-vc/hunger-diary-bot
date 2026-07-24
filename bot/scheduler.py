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
        if not should_send_morning(repo):
            return
        await bot.send_message(
            config.allowed_user_id,
            MSG_MORNING,
            reply_markup=scale_keyboard("hunger", with_cancel=False),
        )
        repo.log_reminder("morning")
        logger.info("Sent morning reminder")

    async def inactivity_job() -> None:
        decision = decide_inactivity(repo, config.sleep_time)
        if decision.kind is None:
            return

        if decision.kind == "inactivity_1":
            text = MSG_INACTIVITY_1
        else:
            text = MSG_INACTIVITY_2

        await bot.send_message(
            config.allowed_user_id,
            text,
            reply_markup=scale_keyboard("hunger", with_cancel=False),
        )
        repo.log_reminder(decision.kind)
        logger.info("Sent %s reminder", decision.kind)

    # Check every minute near wake-up; cheap for one user
    scheduler.add_job(morning_job, CronTrigger(minute="*", timezone=config.timezone))
    scheduler.add_job(inactivity_job, IntervalTrigger(minutes=15))
    return scheduler
