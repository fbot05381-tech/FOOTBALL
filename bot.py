import asyncio
import importlib
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage
from utils.db import init_db

from handlers import match_engine, tournament_mode

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

# Register Routers
dp.include_router(match_engine.router)
dp.include_router(tournament_mode.router)

# Startup Tasks
async def on_startup():
    await init_db()
    logger.info("✅ Database Initialized")

    commands = [
        BotCommand(command="/start_football", description="Start Team Mode"),
        BotCommand(command="/create_tournament", description="Create Tournament"),
        BotCommand(command="/join_tournament", description="Join Tournament"),
        BotCommand(command="/score", description="Show Score"),
        BotCommand(command="/pause_game", description="Pause Game"),
        BotCommand(command="/resume_game", description="Resume Game"),
        BotCommand(command="/pause_tournament", description="Pause Tournament"),
        BotCommand(command="/resume_tournament", description="Resume Tournament"),
        BotCommand(command="/end_tournament", description="End Tournament")
    ]
    await bot.set_my_commands(commands)
    logger.info("✅ Football Bot is running...")

async def main():
    await on_startup()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
