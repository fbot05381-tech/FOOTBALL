import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart

from handlers import match_engine, tournament_mode
from utils.db import init_db
from config import BOT_TOKEN

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# Routers include
dp.include_router(match_engine.router)
dp.include_router(tournament_mode.router)

# ========== Start Football Command ==========
@dp.message(CommandStart())
async def start_cmd(message: Message):
    await message.answer("👋 Welcome to Football Bot!\nUse /start_football to play.")

@dp.message(commands=["start_football"])
async def start_football(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚽ Team Mode", callback_data="team_mode")],
        [InlineKeyboardButton(text="🏆 Tournament Mode", callback_data="tournament_mode")]
    ])
    await message.answer("🎮 Choose a mode:", reply_markup=kb)

@dp.callback_query(lambda c: c.data == "team_mode")
async def team_mode_callback(callback_query: types.CallbackQuery):
    await callback_query.message.answer("✅ Team Mode Selected!\nUse /create_match to start.")

@dp.callback_query(lambda c: c.data == "tournament_mode")
async def tournament_mode_callback(callback_query: types.CallbackQuery):
    await callback_query.message.answer("✅ Tournament Mode Selected!\nUse /create_tournament to start.")

# ========== Startup ==========
async def main():
    await init_db()
    logger.info("🤖 Bot started successfully!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
