import asyncio
import random
import time
from aiogram import Router, types
from aiogram.filters import Command

router = Router()

match_data = {
    "team_a": [],
    "team_b": [],
    "referee": None,
    "started": False,
    "paused": False,
    "score": {"A": 0, "B": 0},
    "stats": {},
    "captains": {},
    "goalkeepers": {},
    "start_time": None,
    "ball_holder": None
}

score_cooldown = 0
command_cooldowns = {}

# ======= Start Team Mode =======
async def start_team_mode(chat_id):
    from main import bot
    msg_a = await bot.send_message(chat_id, "🔵 Join Team A: /join_teamA")
    msg_b = await bot.send_message(chat_id, "🔴 Join Team B: /join_teamB")

    await asyncio.sleep(120)  # 2 minute join time
    await bot.delete_message(chat_id, msg_a.message_id)
    await bot.delete_message(chat_id, msg_b.message_id)

@router.message(Command("join_teamA"))
async def join_team_a(message: types.Message):
    uid = message.from_user.id
    if uid in match_data["team_a"] or uid in match_data["team_b"]:
        return await message.answer("⚠️ Already in a team!")
    match_data["team_a"].append(uid)
    await message.answer(f"✅ {message.from_user.full_name} joined Team A!")

@router.message(Command("join_teamB"))
async def join_team_b(message: types.Message):
    uid = message.from_user.id
    if uid in match_data["team_a"] or uid in match_data["team_b"]:
        return await message.answer("⚠️ Already in a team!")
    match_data["team_b"].append(uid)
    await message.answer(f"✅ {message.from_user.full_name} joined Team B!")

# ======= Referee & Match Commands =======
@router.message(Command("set_referee"))
async def set_referee(message: types.Message):
    match_data["referee"] = message.from_user.id
    await message.answer(f"👨‍⚖️ Referee set: {message.from_user.full_name}")

@router.message(Command("start_match"))
async def start_match(message: types.Message):
    if message.from_user.id != match_data["referee"]:
        return await message.answer("⚠️ Only referee can start the match!")
    match_data["started"] = True
    match_data["start_time"] = time.time()
    await message.answer("🎮 Match Started!")

@router.message(Command("pause_game"))
async def pause_game(message: types.Message):
    if message.from_user.id != match_data["referee"]:
        return await message.answer("⚠️ Only referee can pause!")
    match_data["paused"] = True
    await message.answer("⏸️ Match Paused!")

@router.message(Command("resume_game"))
async def resume_game(message: types.Message):
    if message.from_user.id != match_data["referee"]:
        return await message.answer("⚠️ Only referee can resume!")
    match_data["paused"] = False
    await message.answer("▶️ Match Resumed!")

@router.message(Command("end_match"))
async def end_match(message: types.Message):
    if message.from_user.id != match_data["referee"]:
        return await message.answer("⚠️ Only referee can end match!")
    match_data["started"] = False
    match_data["team_a"].clear()
    match_data["team_b"].clear()
    await message.answer("🏁 Match Ended!")
    
