from aiogram import Router, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

@router.message(Command("start_football"))
async def start_football(message: types.Message):
    kb = InlineKeyboardBuilder()
    kb.button(text="⚽ Team Match Mode", callback_data="start_match_mode")
    kb.button(text="🏆 Tournament Mode", callback_data="start_tournament_mode")
    kb.adjust(1)

    await message.answer(
        "🎮 <b>Football Game Modes</b>\n\nChoose a mode to start:",
        reply_markup=kb.as_markup()
    )

@router.callback_query(lambda c: c.data == "start_match_mode")
async def match_mode_selected(callback: types.CallbackQuery):
    await callback.message.answer("✅ Team Match Mode selected!\nUse /start_match to begin.")
    await callback.answer()

@router.callback_query(lambda c: c.data == "start_tournament_mode")
async def tournament_mode_selected(callback: types.CallbackQuery):
    await callback.message.answer("✅ Tournament Mode selected!\nUse /create_tournament to begin.")
    await callback.answer()
