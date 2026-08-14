from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from bot.config import Config
from bot.keyboards import main_menu
from bot.repositories import Repository
from bot.texts import MSG_START_AGAIN, MSG_START_FIRST, msg_settings

router = Router()


class SettingsStates(StatesGroup):
    waiting_time = State()


@router.message(CommandStart())
async def cmd_start(
    message: Message,
    state: FSMContext,
    repo: Repository,
    user_id: int,
) -> None:
    await state.clear()
    count = repo.count_events(user_id)
    text = MSG_START_FIRST if count == 0 else MSG_START_AGAIN
    await message.answer(text, reply_markup=main_menu())


@router.message(Command("settings"))
async def cmd_settings(
    message: Message,
    state: FSMContext,
    repo: Repository,
    config: Config,
    user_id: int,
) -> None:
    await state.set_state(SettingsStates.waiting_time)
    user_cfg = config.users[user_id]
    settings = repo.get_settings(user_id, default_wake_up=user_cfg.wake_up_time)
    wake = settings.wake_up_time.strftime("%H:%M")
    await message.answer(msg_settings(wake, settings.timezone), reply_markup=main_menu())
