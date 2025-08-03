import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import Message
from config import BOT_TOKEN
from handlers import match_engine
from utils.db import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# ✅ Reminder loop define
async def reminder_loop():
    while True:
        await asyncio.sleep(300)  # हर 5 मिनट में reminder logic
        # यहाँ future reminder logic डाल सकते हो

async def on_startup():
    logger.info("📂 Initializing database...")
    await init_db()
    logger.info("✅ Database initialized.")
    asyncio.create_task(reminder_loop())

# ✅ Commands Register
dp.message.register(match_engine.start_match, F.text.startswith("/start_match"))
dp.message.register(match_engine.add_player, F.text.startswith("/add_player"))
dp.message.register(match_engine.remove_player_a, F.text.startswith("/remove_player_A"))
dp.message.register(match_engine.remove_player_b, F.text.startswith("/remove_player_B"))
dp.message.register(match_engine.pause_game, F.text.startswith("/pause_game"))
dp.message.register(match_engine.resume_game, F.text.startswith("/resume_game"))
dp.message.register(match_engine.show_score, F.text.startswith("/score"))

async def main():
    await on_startup()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
