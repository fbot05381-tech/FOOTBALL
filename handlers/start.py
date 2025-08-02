from aiogram import Router, types
from aiogram.filters import CommandStart

router = Router()

@router.message(CommandStart())
async def start(msg: types.Message):
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="🏟️ Team Mode", callback_data="team_mode")],
        [types.InlineKeyboardButton(text="🏆 Tournament Mode", callback_data="tournament_mode")]
    ])
    await msg.answer("⚽ Welcome to Football Bot!\nChoose a mode:", reply_markup=kb)
