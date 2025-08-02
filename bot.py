import json
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
import logging
import importlib
import os

# Load Config
with open("config.json") as f:
    CONFIG = json.load(f)

BOT_TOKEN = CONFIG["BOT_TOKEN"]

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

# Load Handlers dynamically
for file in os.listdir("handlers"):
    if file.endswith(".py"):
        importlib.import_module(f"handlers.{file[:-3]}")

async def set_commands():
    commands = [
        BotCommand(command="start_football", description="Start Football Bot")
    ]
    await bot.set_my_commands(commands)

async def main():
    await set_commands()
    logging.info("Football Bot is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
