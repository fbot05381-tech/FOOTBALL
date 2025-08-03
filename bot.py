import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.default import DefaultBotProperties

from handlers import match_engine, tournament_mode
from utils.db import init_db

import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

# ✅ Bot Initialization (New Recommended Way)
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Include Routers
dp.include_router(match_engine.router)
dp.include_router(tournament_mode.router)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================= START HANDLER =================

@dp.message(CommandStart())
async def start_cmd(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👥 Team Mode", callback_data="team_mode")],
        [InlineKeyboardButton(text="🏆 Tournament Mode", callback_data="tournament_mode")]
    ])
    await message.answer("⚽ Choose a mode to start:", reply_markup=kb)

# ================= CALLBACK HANDLERS =================

@dp.callback_query()
async def callbacks(call: CallbackQuery):
    if call.data == "team_mode":
        await call.message.answer("✅ Team Mode Selected!\nUse /create_match to start a new match.")
    elif call.data == "tournament_mode":
        await call.message.answer("✅ Tournament Mode Selected!\nUse /create_tournament to start a tournament.")
    await call.answer()

# ================== BOT STARTUP ===================

async def main():
    logger.info("📂 Initializing database...")
    await init_db()
    logger.info("✅ Database initialized.")
    logger.info("🤖 Bot started successfully!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped.")
