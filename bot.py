import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from handlers import match_engine, tournament_mode
from utils.db import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

# ✅ Register Routers
dp.include_router(match_engine.router)
dp.include_router(tournament_mode.router)

async def set_commands():
    commands = [
        BotCommand(command="start_match", description="⚽ Start the football match"),
        BotCommand(command="pause_game", description="⏸ Pause current game"),
        BotCommand(command="resume_game", description="▶ Resume paused game"),
        BotCommand(command="score", description="📊 Show current score"),
        BotCommand(command="time", description="⏱ Show match time left"),
        BotCommand(command="end_match", description="🏁 End current match"),
    ]
    await bot.set_my_commands(commands)

async def on_startup():
    logger.info("📂 Initializing database...")
    try:
        await init_db()
        logger.info("✅ Database initialized.")
    except Exception as e:
        logger.error(f"❌ DB Init Error: {e}")

    # ✅ Reminder loop check
    try:
        from handlers.tournament_mode import reminder_loop
        asyncio.create_task(reminder_loop(bot))
    except ImportError:
        logger.warning("⚠️ reminder_loop not found, skipping...")

    await set_commands()
    logger.info("🤖 Bot started successfully!")

async def main():
    await on_startup()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
