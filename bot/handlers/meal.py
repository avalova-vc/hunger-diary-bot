from __future__ import annotations

import re

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from bot.keyboards import meal_time_keyboard, meal_type_keyboard, scale_keyboard
from bot.repositories import (
    MEAL_LABELS,
    Repository,
    format_local_time,
    meal_datetime_from_hhmm,
    meal_datetime_from_offset,
)
from bot.texts import (
    BTN_MEAL,
    MSG_CANCELLED,
    MSG_HUNGER_BEFORE,
    MSG_MEAL_TIME,
    MSG_MEAL_TIME_BAD,
    MSG_MEAL_TIME_MANUAL,
    MSG_MEAL_TYPE,
    MSG_SATIETY_AFTER,
    msg_meal_saved,
)

router = Router()

TIME_RE = re.compile(r"^([01]?\d|2[0-3]):([0-5]\d)$")

MEAL_TIME_OFFSETS = {"0", "15", "30", "60"}


class MealStates(StatesGroup):
    choose_type = State()
    hunger_before = State()
    satiety_after = State()
    meal_time = State()
    meal_time_manual = State()


async def _save_meal(
    *,
    state: FSMContext,
    repo: Repository,
    user_id: int,
    ate_at,
    reply_target: Message,
) -> None:
    data = await state.get_data()
    event = repo.add_meal(
        user_id,
        data["meal_type"],
        data["hunger_before"],
        data["satiety_after"],
        ate_at,
    )
    hhmm = format_local_time(event.ate_at or event.created_at, repo.timezone_name)
    label = MEAL_LABELS[data["meal_type"]]
    await reply_target.edit_text(
        msg_meal_saved(label, data["hunger_before"], data["satiety_after"], hhmm)
    )
    await state.clear()


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
async def choose_satiety(callback: CallbackQuery, state: FSMContext) -> None:
    assert callback.data is not None
    assert callback.message is not None
    value = callback.data.split(":", 1)[1]

    if value == "cancel":
        await state.clear()
        await callback.message.edit_text(MSG_CANCELLED)
        await callback.answer()
        return

    await state.update_data(satiety_after=int(value))
    await state.set_state(MealStates.meal_time)
    await callback.message.edit_text(MSG_MEAL_TIME, reply_markup=meal_time_keyboard())
    await callback.answer()


@router.callback_query(MealStates.meal_time, F.data.startswith("meal_time:"))
async def choose_meal_time(
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

    if value == "manual":
        await state.set_state(MealStates.meal_time_manual)
        await callback.message.edit_text(MSG_MEAL_TIME_MANUAL)
        await callback.answer()
        return

    if value not in MEAL_TIME_OFFSETS:
        await callback.answer()
        return

    ate_at = meal_datetime_from_offset(int(value))
    await _save_meal(
        state=state,
        repo=repo,
        user_id=user_id,
        ate_at=ate_at,
        reply_target=callback.message,
    )
    await callback.answer()


@router.message(MealStates.meal_time_manual)
async def set_meal_time_manual(
    message: Message,
    state: FSMContext,
    repo: Repository,
    user_id: int,
) -> None:
    text = (message.text or "").strip()
    if not TIME_RE.match(text):
        await message.answer(MSG_MEAL_TIME_BAD)
        return

    hour, minute = text.split(":")
    normalized = f"{int(hour):02d}:{int(minute):02d}"
    ate_at = meal_datetime_from_hhmm(normalized, repo.timezone_name)
    data = await state.get_data()
    event = repo.add_meal(
        user_id,
        data["meal_type"],
        data["hunger_before"],
        data["satiety_after"],
        ate_at,
    )
    hhmm = format_local_time(event.ate_at or event.created_at, repo.timezone_name)
    label = MEAL_LABELS[data["meal_type"]]
    await message.answer(
        msg_meal_saved(label, data["hunger_before"], data["satiety_after"], hhmm)
    )
    await state.clear()
