import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage

from handlers import match_engine, tournament_mode
from utils.db import init_db
from config import BOT_TOKEN

# ✅ Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Bot + Dispatcher
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

# ✅ Commands list (for menu)
async def set_commands():
    commands = [
        BotCommand(command="/start_football", description="Start football match"),
        BotCommand(command="/create_team", description="Create teams"),
        BotCommand(command="/join_football", description="Join football match"),
        BotCommand(command="/score", description="Show current score"),
        BotCommand(command="/time", description="Show remaining time"),
        BotCommand(command="/pause_game", description="Pause current game"),
        BotCommand(command="/resume_game", description="Resume paused game"),
        BotCommand(command="/reset_match", description="Reset current match"),
    ]
    await bot.set_my_commands(commands)

# ✅ Startup
async def on_startup():
    logger.info("📂 Initializing database...")
    await init_db()
    await set_commands()
    logger.info("✅ Database initialized.")
    logger.info("🤖 Bot started successfully!")

# ✅ Routers include
dp.include_router(match_engine.router)
dp.include_router(tournament_mode.router)

# ✅ Main runner
async def main():
    await on_startup()
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("🚫 Bot stopped.")
