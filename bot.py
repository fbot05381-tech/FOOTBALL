import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from handlers import match_engine, tournament_mode
from utils.db import init_db
from utils.reminder import reminder_loop

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

# ✅ Include Routers
dp.include_router(match_engine.router)
dp.include_router(tournament_mode.router)

async def on_startup():
    logger.info("📂 Initializing database...")
    await init_db()
    logger.info("✅ Database initialized.")

    # ✅ Start Reminder Loop
    try:
        asyncio.create_task(reminder_loop(bot))
        logger.info("🔄 Reminder loop started.")
    except Exception as e:
        logger.error(f"⚠️ Failed to start reminder loop: {e}")

async def main():
    await on_startup()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
