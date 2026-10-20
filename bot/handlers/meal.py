from __future__ import annotations

from datetime import datetime

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from bot.keyboards import main_menu, meal_time_keyboard, meal_type_keyboard, scale_keyboard
from bot.repositories import (
    MEAL_LABELS,
    Repository,
    format_local_time,
    parse_meal_hhmm,
    utc_now,
)
from bot.texts import (
    BTN_MEAL,
    MSG_CANCELLED,
    MSG_HUNGER_BEFORE,
    MSG_MEAL_TIME_ASK,
    MSG_MEAL_TIME_BAD,
    MSG_MEAL_TIME_MANUAL,
    MSG_MEAL_TYPE,
    MSG_SATIETY_AFTER,
    msg_meal_saved,
)

router = Router()


class MealStates(StatesGroup):
    choose_type = State()
    hunger_before = State()
    satiety_after = State()
    meal_time = State()
    meal_time_manual = State()


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
async def choose_satiety(callback: CallbackQuery, state: FSMContext, repo: Repository) -> None:
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
    now_hhmm = format_local_time(utc_now(), repo.timezone_name)
    await callback.message.edit_text(
        MSG_MEAL_TIME_ASK,
        reply_markup=meal_time_keyboard(now_hhmm),
    )
    await callback.answer()


@router.callback_query(MealStates.meal_time, F.data.startswith("meal_time:"))
async def choose_meal_time(callback: CallbackQuery, state: FSMContext, repo: Repository) -> None:
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

    await _save_meal(callback, state, repo, utc_now())
    await callback.answer()


@router.message(MealStates.meal_time_manual)
async def enter_meal_time(message: Message, state: FSMContext, repo: Repository) -> None:
    raw = (message.text or "").strip()
    try:
        meal_time = parse_meal_hhmm(raw, repo.timezone_name)
    except ValueError:
        await message.answer(MSG_MEAL_TIME_BAD)
        return

    await _save_meal(message, state, repo, meal_time)


async def _save_meal(
    target: CallbackQuery | Message,
    state: FSMContext,
    repo: Repository,
    meal_time: datetime,
) -> None:
    data = await state.get_data()
    meal_type = data["meal_type"]
    hunger_before = data["hunger_before"]
    satiety_after = data["satiety_after"]

    event = repo.add_meal(meal_type, hunger_before, satiety_after, meal_time)
    hhmm = format_local_time(event.meal_time, repo.timezone_name)
    label = MEAL_LABELS[meal_type]
    text = msg_meal_saved(label, hunger_before, satiety_after, hhmm)
    await state.clear()

    if isinstance(target, CallbackQuery):
        assert target.message is not None
        await target.message.edit_text(text)
    else:
        await target.answer(text, reply_markup=main_menu())
