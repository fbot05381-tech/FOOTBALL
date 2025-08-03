import logging
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.default import DefaultBotProperties

from match_engine import router as match_router
from tournament_mode import router as tournament_router

# ========== CONFIG ==========
from config import BOT_TOKEN

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

# Routers include
dp.include_router(match_router)
dp.include_router(tournament_router)

# ========== Start Command ==========
@dp.message(CommandStart())
async def start_cmd(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚽ Team Mode", callback_data="team_mode")],
        [InlineKeyboardButton(text="🏆 Tournament Mode", callback_data="tournament_mode")]
    ])
    msg = await message.answer("🎮 Choose a mode to start football game:", reply_markup=kb)

# ========== Callback for Mode Selection ==========
@dp.callback_query(F.data == "team_mode")
async def team_mode_selected(callback: CallbackQuery):
    try:
        await callback.message.delete()
    except:
        pass
    await callback.message.answer("✅ Team Mode Selected!\n\nUse /team_mode to start team joining phase (2 min).")

@dp.callback_query(F.data == "tournament_mode")
async def tournament_mode_selected(callback: CallbackQuery):
    try:
        await callback.message.delete()
    except:
        pass
    await callback.message.answer("✅ Tournament Mode Selected!\n\nUse /create_tournament to create tournament and /join_tournament for players.")

# ========== Bot Startup ==========
async def main():
    logger.info("📂 Initializing database...")
    # यहाँ database init code रहेगा
    logger.info("✅ Database initialized.")
    logger.info("🤖 Bot started successfully!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
