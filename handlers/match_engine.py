from aiogram import Router, F
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.db import (
    get_match_data, save_match_data, reset_match_data,
    get_scoreboard_text, add_goal, add_assist, set_last_pass,
    pause_match, resume_match, is_paused
)
import random
import asyncio

router = Router()

# 🔥 Sample GIFs
SCOREBOARD_GIFS = [
    "https://media.giphy.com/media/3o6ZsX2Q3iAFY1n9sM/giphy.gif",
    "https://media.giphy.com/media/l0MYI7xv8sax7Qk52/giphy.gif"
]

TIME_GIFS = [
    "https://media.giphy.com/media/3o6Zt481isNVuQI1l6/giphy.gif",
    "https://media.giphy.com/media/xT0xezQGU5xCDJuCPe/giphy.gif"
]

# ✅ Start Match
@router.message(F.text == "/start_match")
async def start_match(msg: Message):
    data = get_match_data()
    if not data['teams']['A'] or not data['teams']['B']:
        await msg.answer("⚠️ Both teams must have players before starting the match!")
        return
    data['status'] = 'running'
    data['current_round'] = 1
    data['time_left'] = 15 * 60  # 15 minutes per round
    save_match_data(data)
    await msg.answer("🏁 Match Started! 15 minutes Round 1 begins now.")
    await send_scoreboard(msg)

# ✅ Scoreboard
async def send_scoreboard(msg: Message):
    data = get_match_data()
    text = get_scoreboard_text(data)
    gif = random.choice(SCOREBOARD_GIFS)
    await msg.answer_animation(animation=gif, caption=text, parse_mode="HTML")

# ✅ /score Command
@router.message(F.text == "/score")
async def cmd_score(msg: Message):
    await send_scoreboard(msg)

# ✅ /time Command
@router.message(F.text == "/time")
async def cmd_time(msg: Message):
    data = get_match_data()
    mins = data['time_left'] // 60
    secs = data['time_left'] % 60
    gif = random.choice(TIME_GIFS)
    await msg.answer_animation(animation=gif, caption=f"⏳ <b>Time Left:</b> {mins} min {secs} sec", parse_mode="HTML")

# ✅ Pause & Resume
@router.message(F.text == "/pause_game")
async def cmd_pause(msg: Message):
    pause_match()
    await msg.answer("⏸️ <b>Game Paused by Referee!</b>", parse_mode="HTML")
    await send_scoreboard(msg)

@router.message(F.text == "/resume_game")
async def cmd_resume(msg: Message):
    resume_match()
    await msg.answer("▶️ <b>Game Resumed!</b>", parse_mode="HTML")
    await send_scoreboard(msg)

# ✅ Reset Match (Clean Everything)
@router.message(F.text == "/reset_match")
async def cmd_reset(msg: Message):
    reset_match_data()
    await msg.answer("🔄 <b>Match has been fully reset!</b>\nAll teams, scores & timers are cleared.", parse_mode="HTML")
