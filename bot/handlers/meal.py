from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from bot.keyboards import main_menu, meal_type_keyboard, scale_keyboard
from bot.repositories import MEAL_LABELS, Repository, format_local_time
from bot.texts import (
    BTN_MEAL,
    MSG_CANCELLED,
    MSG_HUNGER_BEFORE,
    MSG_MEAL_TYPE,
    MSG_SATIETY_AFTER,
    msg_meal_saved,
)

router = Router()


class MealStates(StatesGroup):
    choose_type = State()
    hunger_before = State()
    satiety_after = State()


@router.message(Command("meal"))
@router.message(F.text == BTN_MEAL)
async def start_meal(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(MealStates.choose_type)
    await message.answer(MSG_MEAL_TYPE, reply_markup=meal_type_keyboard())


@router.callback_query(MealStates.choose_type, F.data.startswith("meal_type:"))
async def choose_type(callback: CallbackQuery, state: FSMContext) -> None:
    assert callback.data is not None
    assert callback.message is not None
    value = callback.data.split(":", 1)[1]

    if value == "cancel":
        await state.clear()
        await callback.message.edit_text(MSG_CANCELLED)
        await callback.answer()
        return

    await state.update_data(meal_type=value)
    await state.set_state(MealStates.hunger_before)
    await callback.message.edit_text(
        MSG_HUNGER_BEFORE,
        reply_markup=scale_keyboard("meal_hunger", with_cancel=True),
    )
    await callback.answer()


@router.callback_query(MealStates.hunger_before, F.data.startswith("meal_hunger:"))
async def choose_hunger_before(callback: CallbackQuery, state: FSMContext) -> None:
    assert callback.data is not None
    assert callback.message is not None
    value = callback.data.split(":", 1)[1]

    if value == "cancel":
        await state.clear()
        await callback.message.edit_text(MSG_CANCELLED)
        await callback.answer()
        return

    await state.update_data(hunger_before=int(value))
    await state.set_state(MealStates.satiety_after)
    await callback.message.edit_text(
        MSG_SATIETY_AFTER,
        reply_markup=scale_keyboard("meal_satiety", with_cancel=True),
    )
    await callback.answer()


@router.callback_query(MealStates.satiety_after, F.data.startswith("meal_satiety:"))
async def choose_satiety(
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

    data = await state.get_data()
    meal_type = data["meal_type"]
    hunger_before = data["hunger_before"]
    satiety_after = int(value)

    event = repo.add_meal(user_id, meal_type, hunger_before, satiety_after)
    hhmm = format_local_time(event.created_at, repo.timezone_name)
    label = MEAL_LABELS[meal_type]
    await callback.message.edit_text(msg_meal_saved(label, hunger_before, satiety_after, hhmm))
    await callback.answer()
    await state.clear()
