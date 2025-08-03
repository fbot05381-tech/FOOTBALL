import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from config import BOT_TOKEN
from handlers import match_engine, tournament_mode
from utils.db import init_db
from utils.reminder import reminder_loop

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

dp.include_router(match_engine.router)
dp.include_router(tournament_mode.router)

async def on_startup():
    try:
        logger.info("📂 Initializing database...")
        await init_db()
        logger.info("✅ Database initialized.")
    except Exception as e:
        logger.error(f"❌ DB Init Error: {e}")

    # ✅ Reminder Loop Start
    asyncio.create_task(reminder_loop(bot))

async def main():
    await on_startup()
    logger.info("🤖 Bot started successfully!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
