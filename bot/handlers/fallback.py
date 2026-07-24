from __future__ import annotations

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.keyboards import main_menu
from bot.texts import MSG_UNKNOWN

router = Router()


@router.message()
async def fallback(message: Message, state: FSMContext) -> None:
    current = await state.get_state()
    if current is not None:
        return
    await message.answer(MSG_UNKNOWN, reply_markup=main_menu())
