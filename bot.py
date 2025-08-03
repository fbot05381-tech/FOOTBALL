import asyncio
import logging
import importlib
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from dotenv import load_dotenv
import os

from utils.db import init_db  # ✅ database init

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Bot & Dispatcher
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# ✅ Handlers import
from handlers import match_engine, tournament_mode
dp.include_router(match_engine.router)
dp.include_router(tournament_mode.router)

async def on_startup():
    logger.info("📂 Initializing database...")
    init_db()  # ✅ NO await here
    logger.info("✅ Database initialized.")
    logger.info("🤖 Bot started successfully!")

async def main():
    await on_startup()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
