import asyncio
import random
import time
from aiogram import Router, types
from aiogram.filters import Command
from utils.db import read_json, write_json, MATCH_DB, PLAYER_DB

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
join_message_id = None
join_deadline = None

# ========== Helper Functions ==========

async def update_scoreboard(message: types.Message):
    table = f"📊 <b>Match Scoreboard</b>\n\n"
    table += f"🔵 Team A: {match_data['score']['A']}\n"
    table += f"🔴 Team B: {match_data['score']['B']}\n"
    await message.answer(table)

async def auto_mvp():
    best = None
    max_score = 0
    for player, stats in match_data["stats"].items():
        score = stats.get("goals", 0) * 2 + stats.get("assists", 0)
        if score > max_score:
            max_score = score
            best = player
    return best

def can_use_command(uid):
    now = time.time()
    if uid not in command_cooldowns:
        command_cooldowns[uid] = now
        return True
    if now - command_cooldowns[uid] >= 10:
        command_cooldowns[uid] = now
        return True
    return False

# ========== Commands ==========

@router.message(Command("create_match"))
async def create_match(message: types.Message):
    global join_message_id, join_deadline
    match_data["team_a"].clear()
    match_data["team_b"].clear()
    match_data["referee"] = message.from_user.id
    match_data["started"] = False
    match_data["score"] = {"A": 0, "B": 0}

    join_deadline = time.time() + 120
    join_msg = await message.answer("👥 Match Created!\nUse /join_teamA or /join_teamB to join (2 min)")
    join_message_id = join_msg.message_id

    await asyncio.sleep(120)
    try:
        await message.chat.delete_message(join_message_id)
    except:
        pass
    await message.answer("⏳ Join time over! Referee can now use /start_match after balancing teams.")

@router.message(Command("join_teamA"))
async def join_team_a(message: types.Message):
    global join_deadline
    if not join_deadline or time.time() > join_deadline:
        return await message.answer("⏳ Join window closed!")
    uid = message.from_user.id
    if uid in match_data["team_a"] or uid in match_data["team_b"]:
        return await message.answer("⚠️ Already joined!")
    match_data["team_a"].append(uid)
    await message.answer(f"✅ {message.from_user.full_name} joined Team A!")

@router.message(Command("join_teamB"))
async def join_team_b(message: types.Message):
    global join_deadline
    if not join_deadline or time.time() > join_deadline:
        return await message.answer("⏳ Join window closed!")
    uid = message.from_user.id
    if uid in match_data["team_a"] or uid in match_data["team_b"]:
        return await message.answer("⚠️ Already joined!")
    match_data["team_b"].append(uid)
    await message.answer(f"✅ {message.from_user.full_name} joined Team B!")

@router.message(Command("set_referee"))
async def set_referee(message: types.Message):
    match_data["referee"] = message.from_user.id
    await message.answer(f"👨‍⚖️ Referee set: {message.from_user.full_name}")

@router.message(Command("start_match"))
async def start_match(message: types.Message):
    if message.from_user.id != match_data["referee"]:
        return await message.answer("⚠️ Only referee can start the match!")
    if not match_data["team_a"] or not match_data["team_b"]:
        return await message.answer("⚠️ Both teams must have players!")

    match_data["started"] = True
    match_data["start_time"] = time.time()
    match_data["ball_holder"] = random.choice(match_data["team_a"] + match_data["team_b"])
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

@router.message(Command("score"))
async def show_score(message: types.Message):
    global score_cooldown
    now = time.time()
    if now - score_cooldown < 30:
        return await message.answer("⏳ Please wait before using /score again!")
    score_cooldown = now
    await update_scoreboard(message)

@router.message(Command("end_match"))
async def end_match(message: types.Message):
    if message.from_user.id != match_data["referee"]:
        return await message.answer("⚠️ Only referee can end the match!")
    mvp = await auto_mvp()
    await message.answer(f"🏁 Match Ended!\nMVP: {mvp}")
    match_data["started"] = False
    match_data["paused"] = False
    match_data["team_a"].clear()
    match_data["team_b"].clear()
    match_data["score"] = {"A": 0, "B": 0}
    match_data["stats"].clear()
