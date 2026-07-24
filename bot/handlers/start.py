from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from bot.keyboards import main_menu
from bot.repositories import Repository
from bot.texts import MSG_START_AGAIN, MSG_START_FIRST, MSG_UNKNOWN, msg_settings

router = Router()


class SettingsStates(StatesGroup):
    waiting_time = State()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, repo: Repository) -> None:
    await state.clear()
    count = repo.count_events()
    text = MSG_START_FIRST if count == 0 else MSG_START_AGAIN
    await message.answer(text, reply_markup=main_menu())


@router.message(Command("settings"))
async def cmd_settings(message: Message, state: FSMContext, repo: Repository) -> None:
    await state.set_state(SettingsStates.waiting_time)
    settings = repo.get_settings()
    wake = settings.wake_up_time.strftime("%H:%M")
    await message.answer(msg_settings(wake, settings.timezone), reply_markup=main_menu())
