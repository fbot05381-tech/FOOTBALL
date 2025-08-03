import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from handlers import match_engine, tournament_mode
from utils.db import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = "YOUR_BOT_TOKEN"

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

async def set_commands():
    commands = [
        BotCommand(command="start_match", description="Start football match"),
        BotCommand(command="pause_game", description="Pause the game"),
        BotCommand(command="resume_game", description="Resume the game"),
        BotCommand(command="reset_match", description="Reset current match"),
        BotCommand(command="score", description="Show current score"),
        BotCommand(command="time", description="Show remaining time"),
        BotCommand(command="add_player", description="Add player to a team"),
        BotCommand(command="remove_player_a", description="Remove player from Team A"),
        BotCommand(command="remove_player_b", description="Remove player from Team B"),
    ]
    await bot.set_my_commands(commands)

async def on_startup():
    logger.info("📂 Initializing database...")
    await init_db()
    logger.info("✅ Database initialized.")
    dp.include_router(match_engine.router)
    dp.include_router(tournament_mode.router)
    await set_commands()
    logger.info("🤖 Bot started successfully!")

async def main():
    await on_startup()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
