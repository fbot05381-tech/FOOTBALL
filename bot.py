import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from match_engine import router as match_router
from tournament_mode import router as tournament_router
from utils.db import init_db
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()

# Routers include
dp.include_router(match_router)
dp.include_router(tournament_router)

# ✅ Start Football Command with 2 Mode Buttons
@dp.message(CommandStart())
async def start_cmd(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚽ Team Mode", callback_data="team_mode")],
        [InlineKeyboardButton(text="🏆 Tournament Mode", callback_data="tournament_mode")]
    ])
    msg = await message.answer("Choose a mode:", reply_markup=kb)

# ✅ Callback for Mode Selection
@dp.callback_query(F.data == "team_mode")
async def team_mode_callback(query: types.CallbackQuery):
    await query.message.delete()
    await query.message.answer("Team Mode selected!\nUse /set_referee to assign referee.\nThen use /join_teamA or /join_teamB (2 min limit).")

@dp.callback_query(F.data == "tournament_mode")
async def tournament_mode_callback(query: types.CallbackQuery):
    await query.message.delete()
    await query.message.answer("Tournament Mode selected!\nUse /create_tournament to start.")

async def main():
    await init_db()
    logging.info("✅ Database initialized.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
