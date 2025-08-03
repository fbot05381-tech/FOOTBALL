import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_TOKEN
from handlers import match_engine, tournament_mode

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# ✅ Include both routers
dp.include_router(match_engine.router)
dp.include_router(tournament_mode.router)

# ========== START FOOTBALL ==========
@dp.message(Command("start_football"))
async def start_football(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚽ Team Mode", callback_data="team_mode")],
        [InlineKeyboardButton(text="🏆 Tournament Mode", callback_data="tournament_mode")]
    ])
    await message.answer("Choose your mode:", reply_markup=kb)

# ========== CALLBACK HANDLER ==========
@dp.callback_query(F.data == "team_mode")
async def team_mode_handler(callback: types.CallbackQuery):
    from handlers.match_engine import send_join_commands
    await send_join_commands(callback.message)

@dp.callback_query(F.data == "tournament_mode")
async def tournament_mode_handler(callback: types.CallbackQuery):
    await callback.message.answer("🏆 Tournament Mode Selected!\nUse /create_tournament to start.")

# ========== STARTUP ==========
async def on_startup():
    logger.info("📂 Initializing database...")

async def main():
    await on_startup()
    logger.info("🤖 Bot started successfully!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
