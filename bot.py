import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import BOT_TOKEN
from handlers import match_engine, tournament_mode
from utils.db import init_db
from utils.reminder import start_reminder_loop

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot init
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

# Include routers
dp.include_router(match_engine.router)
dp.include_router(tournament_mode.router)

# ========== Start Command ==========
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    kb = InlineKeyboardBuilder()
    kb.button(text="🎮 Team Mode", callback_data="team_mode")
    kb.button(text="🏆 Tournament Mode", callback_data="tournament_mode")
    await message.answer("⚽ Choose a mode:", reply_markup=kb.as_markup())

# ========== Callback Handlers ==========
@dp.callback_query(lambda c: c.data == "team_mode")
async def team_mode_start(callback: types.CallbackQuery):
    await callback.message.answer("✅ Team Mode Selected!\nUse /create_match to start a new match.")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "tournament_mode")
async def tournament_mode_start(callback: types.CallbackQuery):
    await callback.message.answer("✅ Tournament Mode Selected!\nUse /create_tournament to create a new tournament.")
    await callback.answer()

# ========== Startup ==========
async def on_startup():
    logger.info("📂 Initializing database...")
    await init_db()
    logger.info("✅ Database initialized.")
    asyncio.create_task(start_reminder_loop(bot))
    logger.info("🤖 Bot started successfully!")

async def main():
    await on_startup()
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
