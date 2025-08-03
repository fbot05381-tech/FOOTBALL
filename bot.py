import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from handlers import match_engine, tournament_mode

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot & Dispatcher
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

# Routers include
dp.include_router(match_engine.router)
dp.include_router(tournament_mode.router)

# ✅ Safe startup function
async def on_startup():
    from utils.db import init_db
    try:
        logger.info("📂 Initializing database...")
        await init_db()
        logger.info("✅ Database initialized.")
    except Exception as e:
        logger.error(f"❌ DB Init Error: {e}")

    # ✅ Start reminder loop safely
    try:
        from handlers.tournament_mode import reminder_loop
        asyncio.create_task(reminder_loop())
        logger.info("🔄 Reminder loop started.")
    except ImportError:
        logger.warning("⚠️ reminder_loop not found, skipping...")

# ✅ Main runner
async def main():
    await on_startup()
    logger.info("🤖 Bot started successfully!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("🚫 Bot stopped.")
