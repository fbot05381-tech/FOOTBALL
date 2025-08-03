import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from config import BOT_TOKEN

from handlers import match_engine, tournament_mode, start_menu

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

async def on_startup():
    logger.info("📂 Initializing database...")
    try:
        from utils.db import init_db
        await init_db()
        logger.info("✅ Database initialized.")
    except Exception as e:
        logger.error(f"❌ DB Init Error: {e}")

    try:
        from utils.reminder import reminder_loop
        asyncio.create_task(reminder_loop(bot))
        logger.info("🔄 Reminder loop started...")
    except ImportError:
        logger.warning("⚠️ reminder_loop not found, skipping...")

async def main():
    await on_startup()

    dp.include_router(start_menu.router)
    dp.include_router(match_engine.router)
    dp.include_router(tournament_mode.router)

    logger.info("🤖 Bot started successfully!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
