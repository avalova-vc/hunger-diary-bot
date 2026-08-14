from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards import main_menu, scale_keyboard
from bot.repositories import Repository, format_local_time
from bot.texts import (
    BTN_HUNGER,
    MSG_CANCELLED,
    MSG_HUNGER_ASK,
    msg_hunger_saved,
)

router = Router()


@router.message(Command("hunger"))
@router.message(F.text == BTN_HUNGER)
async def ask_hunger(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(MSG_HUNGER_ASK, reply_markup=scale_keyboard("hunger", with_cancel=True))


@router.callback_query(F.data.startswith("hunger:"))
async def save_hunger(
    callback: CallbackQuery,
    state: FSMContext,
    repo: Repository,
    user_id: int,
) -> None:
    assert callback.data is not None
    assert callback.message is not None
    value = callback.data.split(":", 1)[1]

    if value == "cancel":
        await state.clear()
        await callback.message.edit_text(MSG_CANCELLED)
        await callback.answer()
        return

    level = int(value)
    event = repo.add_hunger(user_id, level)
    hhmm = format_local_time(event.created_at, repo.timezone_name)
    await callback.message.edit_text(msg_hunger_saved(level, hhmm))
    await callback.answer()
    await state.clear()
