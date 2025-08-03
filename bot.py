import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from aiogram.filters import Command
from config import BOT_TOKEN

from handlers import match_engine, tournament_mode
from utils.db import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

dp.include_router(match_engine.router)
dp.include_router(tournament_mode.router)

# ====== Start Football Command ======
@dp.message(Command("start_football"))
async def start_football(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎮 Team Mode", callback_data="team_mode")],
        [InlineKeyboardButton(text="🏆 Tournament Mode", callback_data="tournament_mode")]
    ])
    await message.answer("⚽ <b>Select Football Mode</b>", reply_markup=kb)

# ====== Callback for Mode Selection ======
@dp.callback_query(F.data == "team_mode")
async def select_team_mode(callback_query):
    from handlers.match_engine import start_match_join_phase
    await callback_query.message.answer("✅ Team Mode Selected!\n⏳ Starting join phase for 2 minutes...")
    await start_match_join_phase(callback_query.message)
    await callback_query.answer()

@dp.callback_query(F.data == "tournament_mode")
async def select_tournament_mode(callback_query):
    from handlers.tournament_mode import start_tournament_join_phase
    await callback_query.message.answer("✅ Tournament Mode Selected!\n⏳ Starting join phase for 2 minutes...")
    await start_tournament_join_phase(callback_query.message)
    await callback_query.answer()

# ====== Startup ======
async def on_startup():
    logger.info("📂 Initializing database...")
    await init_db()
    logger.info("✅ Database initialized.")

async def main():
    await on_startup()
    logger.info("🤖 Bot started successfully!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
