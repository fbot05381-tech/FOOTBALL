import asyncio
import logging
from aiogram import Bot, Dispatcher, F, Router
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from utils.db import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

# ✅ Test Router to verify bot response
test_router = Router()

@test_router.message(F.text == "/start")
async def start_cmd(msg: Message):
    await msg.answer("✅ Bot Active Hai! ⚽")

dp.include_router(test_router)

# ✅ Startup function
async def on_startup():
    logger.info("📂 Initializing database...")
    await init_db()
    logger.info("✅ Database initialized.")

async def main():
    await on_startup()
    logger.info("🤖 Bot started successfully!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
