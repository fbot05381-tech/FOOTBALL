import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from match_engine import router as match_router
from tournament_mode import router as tournament_router

API_TOKEN = "YOUR_BOT_TOKEN"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher()

# ✅ Register routers
dp.include_router(match_router)
dp.include_router(tournament_router)

# ========== START FOOTBALL ==========
@dp.message(Command("start_football"))
async def start_football(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚽ Team Mode", callback_data="team_mode")],
        [InlineKeyboardButton(text="🏆 Tournament Mode", callback_data="tournament_mode")]
    ])
    msg = await message.answer("Choose a mode:", reply_markup=kb)

    # Store message ID to delete later
    dp['mode_select_msg'] = msg.message_id

# ========== CALLBACK HANDLER ==========
@dp.callback_query(F.data == "team_mode")
async def team_mode_selected(callback: types.CallbackQuery):
    # ✅ Delete the buttons message
    try:
        await callback.message.delete()
    except:
        pass

    # ✅ Import match_engine start
    await callback.message.answer("⚽ Team Mode Selected!\nUse /create_match to start team joining.")

@dp.callback_query(F.data == "tournament_mode")
async def tournament_mode_selected(callback: types.CallbackQuery):
    # ✅ Delete the buttons message
    try:
        await callback.message.delete()
    except:
        pass

    await callback.message.answer("🏆 Tournament Mode Selected!\nUse /create_tournament to start tournament joining.")

# ========== BOT START ==========
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
