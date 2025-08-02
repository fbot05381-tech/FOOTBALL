import asyncio
import logging
import importlib
import os
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

# ✅ Tumhara bot token direct yahan daal diya
BOT_TOKEN = "8237073959:AAGoZT6Th4nhLF2t_QgXmqnRMqvKQgMYS70"

# Logging enable
logging.basicConfig(level=logging.INFO)

# Bot aur Dispatcher setup
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

# ✅ Handlers auto import (handlers/ folder ke sabhi files)
for file in os.listdir("handlers"):
    if file.endswith(".py"):
        importlib.import_module(f"handlers.{file[:-3]}")

# ✅ Commands set karne ka function
async def set_commands():
    commands = [BotCommand(command="start_football", description="Start Football Bot")]
    await bot.set_my_commands(commands)

# ✅ Main function
async def main():
    await set_commands()
    logging.info("✅ Football Bot is running...")
    await dp.start_polling(bot)

# ✅ Script entry
if __name__ == "__main__":
    asyncio.run(main())
