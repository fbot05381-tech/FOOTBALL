import logging, importlib, os, asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TOKEN_HERE")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

# ✅ Auto load all handlers
for file in os.listdir("handlers"):
    if file.endswith(".py"):
        importlib.import_module(f"handlers.{file[:-3]}")

async def set_commands():
    commands = [
        BotCommand(command="start_football", description="Start Football Mode"),
        BotCommand(command="create_team", description="Create Teams"),
        BotCommand(command="add_member", description="Add Member Manually"),
        BotCommand(command="shift_member", description="Shift Member"),
        BotCommand(command="start_match", description="Start Match"),
        BotCommand(command="end_match", description="End Match"),
        BotCommand(command="captain", description="Choose Captain"),
        BotCommand(command="gk", description="Set Goalkeeper"),
        BotCommand(command="change_gk", description="Change Goalkeeper")
    ]
    await bot.set_my_commands(commands)

async def main():
    await set_commands()
    logger.info("✅ Football Bot is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
