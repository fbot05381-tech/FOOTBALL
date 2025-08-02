import os, asyncio, importlib
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from handlers.tournament_mode import router as tournament_router, reminder_loop
from handlers.team_mode import router as team_router

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# ✅ Register routers
dp.include_router(team_router)
dp.include_router(tournament_router)

# ✅ Start command with mode selection
@dp.message(CommandStart())
async def start_command(msg: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚽ Team Mode", callback_data="team_mode")],
        [InlineKeyboardButton(text="🏆 Tournament Mode", callback_data="tournament_mode")]
    ])
    await msg.answer("Welcome to Football Bot!\nChoose a mode:", reply_markup=kb)

# ✅ Background tasks (Reminder Loop)
async def on_startup():
    asyncio.create_task(reminder_loop(bot))

async def main():
    await on_startup()
    print("✅ Football Bot is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
