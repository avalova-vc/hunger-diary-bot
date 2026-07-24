from __future__ import annotations

import re

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.handlers.start import SettingsStates
from bot.keyboards import main_menu
from bot.repositories import Repository
from bot.texts import MSG_SETTINGS_BAD, msg_settings_updated

router = Router()

TIME_RE = re.compile(r"^([01]?\d|2[0-3]):([0-5]\d)$")


@router.message(SettingsStates.waiting_time)
async def set_wake_up(message: Message, state: FSMContext, repo: Repository) -> None:
    text = (message.text or "").strip()
    if not TIME_RE.match(text):
        await message.answer(MSG_SETTINGS_BAD)
        return

    hour, minute = text.split(":")
    normalized = f"{int(hour):02d}:{int(minute):02d}"
    wake = repo.update_wake_up_time(normalized)
    await state.clear()
    await message.answer(msg_settings_updated(wake), reply_markup=main_menu())
