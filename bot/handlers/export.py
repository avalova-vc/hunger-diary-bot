from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, Message

from bot.config import Config
from bot.keyboards import main_menu
from bot.repositories import Repository
from bot.services.export_csv import export_events_to_csv
from bot.texts import BTN_EXPORT, MSG_EXPORT_EMPTY, MSG_EXPORT_START, msg_export_ok

router = Router()


@router.message(Command("export"))
@router.message(F.text == BTN_EXPORT)
async def export_data(message: Message, state: FSMContext, repo: Repository, config: Config) -> None:
    await state.clear()
    await message.answer(MSG_EXPORT_START)

    path, count = export_events_to_csv(repo, config.exports_dir)
    if path is None:
        await message.answer(MSG_EXPORT_EMPTY, reply_markup=main_menu())
        return

    await message.answer_document(
        FSInputFile(path),
        caption=msg_export_ok(count),
        reply_markup=main_menu(),
    )
