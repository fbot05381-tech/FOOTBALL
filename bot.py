import asyncio
import logging
from aiogram import Bot, Dispatcher, F, Router
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from handlers import match_engine, tournament_mode
from utils.db import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

# ✅ Test Router (to check bot reply)
test_router = Router()

@test_router.message(F.text == "/start")
async def start_cmd(msg: Message):
    await msg.answer("✅ Bot Active Hai! ⚽")

dp.include_router(test_router)

# ✅ Include main game handlers
dp.include_router(match_engine.router)
dp.include_router(tournament_mode.router)

# ✅ Startup
async def on_startup():
    logger.info("📂 Initializing database...")
    try:
        await init_db()
        logger.info("✅ Database initialized.")
    except Exception as e:
        logger.error(f"❌ DB Init Error: {e}")

    # ✅ Reminder loop safe call
    try:
        from utils.reminder import reminder_loop
        asyncio.create_task(reminder_loop(bot))
    except ImportError:
        logger.warning("⚠️ reminder_loop not found, skipping...")

async def main():
    await on_startup()
    logger.info("🤖 Bot started successfully!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
