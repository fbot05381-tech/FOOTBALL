import asyncio
import importlib
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters import CommandStart
from dotenv import load_dotenv

from utils.db import init_db

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# ✅ Startup पर DB initialize
async def on_startup():
    init_db()
    logger.info("✅ Database initialized")

# ✅ Routers load
from handlers.match_engine import router as match_router
from handlers.tournament_mode import router as tournament_router

dp.include_router(match_router)
dp.include_router(tournament_router)

# ✅ Basic Ping Command
@dp.message(CommandStart())
async def start_cmd(msg: Message):
    await msg.answer("⚽ Football Bot is Live!\nUse /start_football to begin!")

async def main():
    await on_startup()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
