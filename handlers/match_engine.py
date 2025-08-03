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

@router.message(Command("start_match"))
async def start_match(message: types.Message):
    if match_data["referee"] and message.from_user.id != match_data["referee"]:
        return await message.answer("⚠️ Only referee can start the match!")

    match_data["started"] = True
    match_data["start_time"] = time.time()
    match_data["ball_holder"] = random.choice(match_data["team_a"] + match_data["team_b"]) if match_data["team_a"] and match_data["team_b"] else None
    await message.answer("🎮 Match Started!")

@router.message(Command("pause_game"))
async def pause_game(message: types.Message):
    if message.from_user.id != match_data["referee"]:
        return await message.answer("⚠️ Only referee can pause the match!")

    match_data["paused"] = True
    await message.answer("⏸️ Match Paused! (Pinned)")
    await message.pin()

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

@router.message(Command("set_referee"))
async def set_referee(message: types.Message):
    if not message.entities or len(message.entities) < 2:
        return await message.answer("⚠️ Use /set_referee @username")
    match_data["referee"] = message.from_user.id
    await message.answer(f"👨‍⚖️ Referee set: {message.from_user.full_name}")

@router.message(Command("add_player"))
async def add_player(message: types.Message):
    if message.from_user.id != match_data["referee"]:
        return await message.answer("⚠️ Only referee can add players!")

    if not message.entities or len(message.entities) < 2:
        return await message.answer("⚠️ Tag a user or provide @username to add!")
    
    team_choice = "A" if len(match_data["team_a"]) <= len(match_data["team_b"]) else "B"
    user_id = message.reply_to_message.from_user.id if message.reply_to_message else message.from_user.id
    if team_choice == "A":
        match_data["team_a"].append(user_id)
    else:
        match_data["team_b"].append(user_id)

    await message.answer(f"✅ Player added to Team {team_choice}!")

@router.message(Command("remove_player_A"))
async def remove_player_a(message: types.Message):
    if message.from_user.id != match_data["referee"]:
        return await message.answer("⚠️ Only referee can remove players!")
    args = message.text.split()
    if len(args) < 2:
        return await message.answer("⚠️ Usage: /remove_player_A <number>")
    try:
        index = int(args[1]) - 1
        if 0 <= index < len(match_data["team_a"]):
            removed = match_data["team_a"].pop(index)
            await message.answer(f"❌ Removed player {removed} from Team A!")
        else:
            await message.answer("⚠️ Invalid number!")
    except:
        await message.answer("⚠️ Invalid input!")

@router.message(Command("remove_player_B"))
async def remove_player_b(message: types.Message):
    if message.from_user.id != match_data["referee"]:
        return await message.answer("⚠️ Only referee can remove players!")
    args = message.text.split()
    if len(args) < 2:
        return await message.answer("⚠️ Usage: /remove_player_B <number>")
    try:
        index = int(args[1]) - 1
        if 0 <= index < len(match_data["team_b"]):
            removed = match_data["team_b"].pop(index)
            await message.answer(f"❌ Removed player {removed} from Team B!")
        else:
            await message.answer("⚠️ Invalid number!")
    except:
        await message.answer("⚠️ Invalid input!")

@router.message(Command("end_match"))
async def end_match(message: types.Message):
    if message.from_user.id != match_data["referee"]:
        return await message.answer("⚠️ Only referee can end the match!")

    mvp = await auto_mvp()
    await message.answer(f"🏁 Match Ended!\nMVP: {mvp}")

    match_data["started"] = False
    match_data["paused"] = False
    match_data["score"] = {"A": 0, "B": 0}
    match_data["stats"].clear()
    match_data["team_a"].clear()
    match_data["team_b"].clear()
    match_data["ball_holder"] = None
