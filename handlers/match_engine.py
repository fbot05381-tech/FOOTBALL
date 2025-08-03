import asyncio
import random
import time
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.utils.markdown import hbold
from utils.db import read_json, write_json, MATCH_DB, PLAYER_DB

router = Router()

# Cooldown Trackers
command_cooldowns = {}
score_cooldown = {}

# Match State
match_data = {
    "team_a": [],
    "team_b": [],
    "referee": None,
    "paused": False,
    "current_ball": None,
    "score": {"A": 0, "B": 0},
    "stats": {},
    "captains": {},
    "goalkeepers": {},
    "start_time": None
}

# ========== Helper Functions ==========

def check_cooldown(user_id, cmd, seconds):
    now = time.time()
    if cmd in command_cooldowns and user_id in command_cooldowns[cmd]:
        if now - command_cooldowns[cmd][user_id] < seconds:
            return False
    command_cooldowns.setdefault(cmd, {})[user_id] = now
    return True

def check_score_cooldown():
    now = time.time()
    if "score" in score_cooldown and now - score_cooldown["score"] < 30:
        return False
    score_cooldown["score"] = now
    return True

async def update_scoreboard(message: types.Message):
    table = f"""
🏆 <b>Scoreboard</b>
Team A: {match_data['score']['A']}
Team B: {match_data['score']['B']}
    """
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

# ========== Commands ==========

@router.message(Command("create_team"))
async def create_team(message: types.Message):
    match_data["team_a"].clear()
    match_data["team_b"].clear()
    match_data["referee"] = message.from_user.id
    match_data["paused"] = False
    match_data["score"] = {"A": 0, "B": 0}
    match_data["stats"].clear()
    await message.answer("✅ Teams created!\nUse /join_football to join Team A or B")

@router.message(Command("join_football"))
async def join_football(message: types.Message):
    user = message.from_user.full_name
    uid = message.from_user.id

    if uid in match_data["team_a"] or uid in match_data["team_b"]:
        await message.answer("⚠️ You are already in a team!")
        return

    if len(match_data["team_a"]) <= len(match_data["team_b"]):
        match_data["team_a"].append(uid)
        team = "A"
    else:
        match_data["team_b"].append(uid)
        team = "B"

    await message.answer(f"✅ {user} joined Team {team}!")

@router.message(Command("start_match"))
async def start_match(message: types.Message):
    if message.from_user.id != match_data["referee"]:
        await message.answer("⚠️ Only referee can start the match!")
        return

    match_data["current_ball"] = random.choice(match_data["team_a"] + match_data["team_b"])
    match_data["start_time"] = time.time()
    await message.answer(f"🎮 Match Started!\n⚽ Ball with <b>{match_data['current_ball']}</b>")

@router.message(Command("pause_game"))
async def pause_game(message: types.Message):
    if message.from_user.id != match_data["referee"]:
        await message.answer("⚠️ Only referee can pause!")
        return

    match_data["paused"] = True
    await message.answer("⏸️ Game Paused! (Pinned)", disable_notification=True)
    await message.pin()

@router.message(Command("resume_game"))
async def resume_game(message: types.Message):
    if message.from_user.id != match_data["referee"]:
        await message.answer("⚠️ Only referee can resume!")
        return

    match_data["paused"] = False
    await message.answer("▶️ Game Resumed!")

@router.message(Command("score"))
async def score_cmd(message: types.Message):
    if not check_score_cooldown():
        await message.answer("⏳ Please wait before using /score again!")
        return
    await update_scoreboard(message)

@router.message(Command("add_player"))
async def add_player(message: types.Message):
    if message.from_user.id != match_data["referee"]:
        return await message.answer("⚠️ Only referee can add players!")
    if not message.entities or len(message.entities) < 2:
        return await message.answer("Usage: /add_player @username")

    uid = message.entities[1].user.id
    if len(match_data["team_a"]) <= len(match_data["team_b"]):
        match_data["team_a"].append(uid)
        team = "A"
    else:
        match_data["team_b"].append(uid)
        team = "B"
    await message.answer(f"✅ Player added to Team {team}!")

@router.message(Command("remove_player_A"))
async def remove_player_a(message: types.Message):
    if message.from_user.id != match_data["referee"]:
        return
    try:
        idx = int(message.text.split()[1]) - 1
        uid = match_data["team_a"].pop(idx)
        await message.answer(f"❌ Removed from Team A: {uid}")
    except:
        await message.answer("⚠️ Invalid index!")

@router.message(Command("remove_player_B"))
async def remove_player_b(message: types.Message):
    if message.from_user.id != match_data["referee"]:
        return
    try:
        idx = int(message.text.split()[1]) - 1
        uid = match_data["team_b"].pop(idx)
        await message.answer(f"❌ Removed from Team B: {uid}")
    except:
        await message.answer("⚠️ Invalid index!")

@router.message(Command("end_match"))
async def end_match(message: types.Message):
    if message.from_user.id != match_data["referee"]:
        await message.answer("⚠️ Only referee can end match!")
        return

    mvp = await auto_mvp()
    await message.answer(f"🏁 Match Ended!\nMVP: {mvp}")
    match_data["paused"] = False
    match_data["team_a"].clear()
    match_data["team_b"].clear()
    match_data["stats"].clear()
