import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import match_engine, tournament_mode
from utils.db import init_db
import os

# ✅ Bot Token from environment
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Bot initialization
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

# ✅ Register routers
dp.include_router(match_engine.router)
dp.include_router(tournament_mode.router)

# ✅ Startup event
async def on_startup():
    logger.info("📂 Initializing database...")
    init_db()  # ✅ अब await नहीं करना है
    logger.info("✅ Database initialized.")

    # ✅ Set default bot commands
    commands = [
        BotCommand(command="/start_football", description="Start a football match"),
        BotCommand(command="/join_football", description="Join football match"),
        BotCommand(command="/create_tournament", description="Create a tournament"),
        BotCommand(command="/join_tournament", description="Join tournament"),
        BotCommand(command="/score", description="Show scoreboard"),
        BotCommand(command="/pause_game", description="Pause ongoing game"),
        BotCommand(command="/resume_game", description="Resume paused game"),
        BotCommand(command="/reset_match", description="Reset match data"),
    ]
    await bot.set_my_commands(commands)
    logger.info("🤖 Bot started successfully!")

# ✅ Main entry point
async def main():
    await on_startup()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
