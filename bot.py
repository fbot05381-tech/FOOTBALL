import asyncio
import logging
import importlib
import os
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

BOT_TOKEN = "8237073959:AAGoZT6Th4nhLF2t_QgXmqnRMqvKQgMYS70"

logging.basicConfig(level=logging.INFO)
logging.info("🚀 Starting Football Bot...")

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

# ✅ Handlers import
handlers_path = "handlers"
logging.info(f"📂 Loading handlers from {handlers_path}")
for file in os.listdir(handlers_path):
    if file.endswith(".py"):
        module = f"handlers.{file[:-3]}"
        importlib.import_module(module)
        logging.info(f"✅ Loaded handler: {module}")

async def set_commands():
    commands = [BotCommand(command="start_football", description="Start Football Bot")]
    await bot.set_my_commands(commands)
    logging.info("✅ Commands registered")

async def main():
    await set_commands()
    logging.info("✅ Football Bot is running and polling started...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
