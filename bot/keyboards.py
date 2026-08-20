from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

from bot.texts import BTN_EXPORT, BTN_HUNGER, BTN_MEAL


def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_HUNGER), KeyboardButton(text=BTN_MEAL)],
            [KeyboardButton(text=BTN_EXPORT)],
        ],
        resize_keyboard=True,
    )


def scale_keyboard(prefix: str, *, with_cancel: bool = True) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=str(i), callback_data=f"{prefix}:{i}") for i in range(0, 6)],
        [InlineKeyboardButton(text=str(i), callback_data=f"{prefix}:{i}") for i in range(6, 11)],
    ]
    if with_cancel:
        rows.append([InlineKeyboardButton(text="Отмена", callback_data=f"{prefix}:cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def meal_type_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Завтрак", callback_data="meal_type:breakfast"),
                InlineKeyboardButton(text="Перекус", callback_data="meal_type:snack"),
            ],
            [
                InlineKeyboardButton(text="Обед", callback_data="meal_type:lunch"),
                InlineKeyboardButton(text="Ужин", callback_data="meal_type:dinner"),
            ],
            [InlineKeyboardButton(text="Отмена", callback_data="meal_type:cancel")],
        ]
    )


def meal_time_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Сейчас", callback_data="meal_time:0")],
            [
                InlineKeyboardButton(text="15 мин назад", callback_data="meal_time:15"),
                InlineKeyboardButton(text="30 мин назад", callback_data="meal_time:30"),
            ],
            [InlineKeyboardButton(text="1 час назад", callback_data="meal_time:60")],
            [InlineKeyboardButton(text="Ввести время", callback_data="meal_time:manual")],
            [InlineKeyboardButton(text="Отмена", callback_data="meal_time:cancel")],
        ]
    )
