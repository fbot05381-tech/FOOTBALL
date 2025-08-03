import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties

# ✅ Import handlers
from handlers import team_mode, tournament_mode
from utils.db import init_db

logging.basicConfig(level=logging.INFO)

# ✅ Your Bot Token
BOT_TOKEN = "8237073959:AAGoZT6Th4nhLF2t_QgXmqnRMqvKQgMYS70"

# ✅ Create Bot & Dispatcher
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# ✅ Include Routers (Handlers)
dp.include_router(team_mode.router)
dp.include_router(tournament_mode.router)

# ✅ Test Command to verify bot is running
@dp.message(Command("start_football"))
async def start_football(msg: Message):
    await msg.answer("🏆 Football Bot is Running and Ready!")

# ✅ Catch All Messages (Debug Mode)
@dp.message()
async def catch_all(msg: Message):
    logging.info(f"📩 Received message: {msg.text}")
    await msg.answer("✅ Bot received your message!")

# ✅ Main Function
async def main():
    init_db()
    logging.info("✅ Football Bot is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
