import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode
from config import BOT_TOKEN

# Handlers import
from handlers import match_engine, tournament_mode

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# ✅ Start Command
@dp.message(Command("start_football"))
async def start_football(message: Message):
    kb = InlineKeyboardBuilder()
    kb.button(text="⚽ Team Mode", callback_data="team_mode")
    kb.button(text="🏆 Tournament Mode", callback_data="tournament_mode")
    await message.answer("🎮 <b>Select Game Mode:</b>", reply_markup=kb.as_markup())

# ✅ Callback for Team Mode
@dp.callback_query(F.data == "team_mode")
async def team_mode_start(callback: CallbackQuery):
    from handlers.match_engine import start_team_join_phase
    await start_team_join_phase(callback.message)

# ✅ Callback for Tournament Mode
@dp.callback_query(F.data == "tournament_mode")
async def tournament_mode_start(callback: CallbackQuery):
    from handlers.tournament_mode import start_tournament_join_phase
    await start_tournament_join_phase(callback.message)

# Include Routers
dp.include_router(match_engine.router)
dp.include_router(tournament_mode.router)

# Startup
async def main():
    logger.info("📂 Initializing database...")
    from utils.db import init_db
    await init_db()
    logger.info("✅ Database initialized.")

    logger.info("🤖 Bot started successfully!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
