import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.enums.parse_mode import ParseMode
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from match_engine import router as match_router, start_team_mode
from tournament_mode import router as tournament_router

from config import BOT_TOKEN

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# Include routers
dp.include_router(match_router)
dp.include_router(tournament_router)

# ========== Start Football ==========
@dp.message(Command("start_football"))
async def start_football(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚽ Team Mode", callback_data="team_mode")],
        [InlineKeyboardButton(text="🏆 Tournament Mode", callback_data="tournament_mode")]
    ])
    await message.answer("Choose Mode:", reply_markup=kb)

# ========== Callback for Modes ==========
@dp.callback_query(F.data == "team_mode")
async def team_mode_callback(callback: types.CallbackQuery):
    await callback.message.delete()  # Delete mode selection message
    await callback.message.answer("🔵 Team Mode Selected!\nPlayers have 2 minutes to join teams.")
    await start_team_mode(callback.message.chat.id)

@dp.callback_query(F.data == "tournament_mode")
async def tournament_mode_callback(callback: types.CallbackQuery):
    await callback.message.delete()  # Delete mode selection message
    await callback.message.answer("🏆 Tournament Mode Selected!\nUse /create_tournament to begin.")

# ========== Bot Startup ==========
async def main():
    logging.info("🤖 Bot Starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
