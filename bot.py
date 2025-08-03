import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from dotenv import load_dotenv
import os

from utils.db import init_db

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# ✅ Import routers
from handlers import match_engine, tournament_mode
dp.include_router(match_engine.router)
dp.include_router(tournament_mode.router)

async def on_startup():
    logger.info("📂 Initializing database...")
    init_db()
    logger.info("✅ Database initialized.")
    logger.info("🤖 Bot started successfully!")

    # ✅ Commands register
    await bot.set_my_commands([
        {"command": "start_football", "description": "⚽ Start a football match"},
        {"command": "pause_game", "description": "⏸ Pause the game"},
        {"command": "resume_game", "description": "▶️ Resume the game"},
        {"command": "score", "description": "📊 Show current score"},
        {"command": "time", "description": "⏱ Show remaining time"},
        {"command": "add_player", "description": "➕ Add a player"},
        {"command": "remove_player_a", "description": "➖ Remove player from Team A"},
        {"command": "remove_player_b", "description": "➖ Remove player from Team B"},
        {"command": "set_referee", "description": "👨‍⚖️ Set referee"},
        {"command": "end_match", "description": "🏁 End current match"}
    ])

async def main():
    await on_startup()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
