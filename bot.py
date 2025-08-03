import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import BOT_TOKEN
from handlers import match_engine, tournament_mode
from utils.db import init_db
from utils.reminder import reminder_loop

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# ✅ Start Command with Team Mode & Tournament Mode
@dp.message(F.text == "/start_football")
async def start_football(message: Message):
    kb = InlineKeyboardBuilder()
    kb.button(text="⚽ Team Mode", callback_data="team_mode")
    kb.button(text="🏆 Tournament Mode", callback_data="tournament_mode")
    await message.answer("Choose Mode:", reply_markup=kb.as_markup())

# ✅ Handle Mode Selection
@dp.callback_query(F.data == "team_mode")
async def team_mode_callback(callback: CallbackQuery):
    from handlers.match_engine import start_team_join
    await start_team_join(callback.message)

@dp.callback_query(F.data == "tournament_mode")
async def tournament_mode_callback(callback: CallbackQuery):
    await callback.message.answer("🏆 Use /create_tournament to start a Tournament")

# ✅ Include Routers
dp.include_router(match_engine.router)
dp.include_router(tournament_mode.router)

async def on_startup():
    logger.info("📂 Initializing database...")
    await init_db()
    logger.info("✅ Database initialized.")
    asyncio.create_task(reminder_loop())

async def main():
    await on_startup()
    logger.info("🤖 Bot started successfully!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
