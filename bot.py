import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN

from handlers import match_engine, tournament_mode

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())


async def set_commands():
    commands = [
        BotCommand(command="start_match", description="⚽ Start Football Match"),
        BotCommand(command="pause_game", description="⏸ Pause Game"),
        BotCommand(command="resume_game", description="▶️ Resume Game"),
        BotCommand(command="reset_match", description="🔄 Reset Match"),
        BotCommand(command="score", description="📊 Show Scoreboard"),
        BotCommand(command="time", description="⏱ Show Time Left"),
    ]
    await bot.set_my_commands(commands)


async def on_startup():
    from utils.db import init_db
    try:
        logger.info("📂 Initializing database...")
        init_db()  # ✅ await हटा दिया
        logger.info("✅ Database initialized.")
    except Exception as e:
        logger.error(f"❌ DB Init Error: {e}")

    try:
        from handlers.tournament_mode import reminder_loop
        asyncio.create_task(reminder_loop())
        logger.info("🔄 Reminder loop started.")
    except ImportError:
        logger.warning("⚠️ reminder_loop not found, skipping...")

    await set_commands()


async def main():
    dp.include_router(match_engine.router)
    dp.include_router(tournament_mode.router)
    await on_startup()
    logger.info("🤖 Bot started successfully!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
