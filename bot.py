import asyncio
import importlib
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.utils.markdown import hbold
from utils.db import load_team_data, save_team_data, load_tournament_data, save_tournament_data

# ✅ Bot Token from Environment
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN not found. Set it in Render Environment Variables.")

# ✅ Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Bot & Dispatcher
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# ✅ Startup Task (Database Check)
async def on_startup():
    os.makedirs("database", exist_ok=True)
    for file in ["database/team_data.json", "database/tournament_data.json"]:
        if not os.path.exists(file):
            with open(file, "w") as f:
                f.write("{}")
    logger.info("✅ Football Bot is running...")

# ✅ Start Command
@dp.message(CommandStart())
async def start_command(message: Message):
    await message.answer(f"👋 Hello {hbold(message.from_user.first_name)}!\n\n"
                         "⚽ Use /start_football for Team Mode\n"
                         "🏆 Use /create_tournament for Tournament Mode")

# ✅ Auto Import All Handlers
for file in os.listdir("handlers"):
    if file.endswith(".py"):
        importlib.import_module(f"handlers.{file[:-3]}")

# ✅ Main Runner
async def main():
    await on_startup()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
