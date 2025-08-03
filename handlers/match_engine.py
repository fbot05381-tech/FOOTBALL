import asyncio
import json
import time
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from utils.db import load_team_data, save_team_data
from utils.helpers import cooldown_check, set_cooldown, format_time

router = Router()

# ✅ TEAM MODE: Create Team
@router.message(Command("create_team"))
async def create_team(msg: Message):
    data = load_team_data()
    chat_id = str(msg.chat.id)

    data[chat_id] = {
        "referee": msg.from_user.id,
        "team_a": [],
        "team_b": [],
        "score_a": 0,
        "score_b": 0,
        "round": 1,
        "match_paused": False,
        "paused_at": None,
        "time_left": 15 * 60,
        "start_time": None,
        "cooldowns": {}
    }
    save_team_data(data)
    await msg.answer("✅ Team mode created!\nUse /join_football to join within 2 minutes.")

# ✅ TEAM MODE: Join Football
@router.message(Command("join_football"))
async def join_team(msg: Message):
    data = load_team_data()
    chat_id = str(msg.chat.id)

    if chat_id not in data:
        return await msg.answer("❌ No active team mode. Use /create_team first.")

    user_id = msg.from_user.id
    if user_id in data[chat_id]["team_a"] or user_id in data[chat_id]["team_b"]:
        return await msg.answer("⚠️ You are already in a team.")

    if len(data[chat_id]["team_a"]) <= len(data[chat_id]["team_b"]):
        data[chat_id]["team_a"].append(user_id)
        team = "A"
    else:
        data[chat_id]["team_b"].append(user_id)
        team = "B"

    save_team_data(data)
    await msg.answer(f"✅ {msg.from_user.full_name} joined Team {team}!")

# ✅ TEAM MODE: Start Match
@router.message(Command("start_match"))
async def start_match(msg: Message):
    data = load_team_data()
    chat_id = str(msg.chat.id)

    if chat_id not in data:
        return await msg.answer("❌ No active match.")

    if msg.from_user.id != data[chat_id]["referee"]:
        return await msg.answer("❌ Only referee can start the match.")

    data[chat_id]["start_time"] = time.time()
    save_team_data(data)

    await msg.answer("🏆 Match started!\nUse /pause_match to pause.")

# ✅ TEAM MODE: Pause Match
@router.message(Command("pause_match"))
async def pause_match(msg: Message):
    data = load_team_data()
    chat_id = str(msg.chat.id)

    if chat_id not in data:
        return await msg.answer("❌ No active match.")

    match = data[chat_id]
    if msg.from_user.id != match["referee"]:
        return await msg.answer("❌ Only referee can pause the match.")

    if match["match_paused"]:
        return await msg.answer("⚠️ Match is already paused.")

    elapsed = time.time() - match["start_time"]
    match["time_left"] -= elapsed
    match["match_paused"] = True
    match["paused_at"] = time.time()
    save_team_data(data)

    await msg.answer(f"⏸️ Match paused!\n⏱️ Time left: {format_time(match['time_left'])}")

# ✅ TEAM MODE: Resume Match
@router.message(Command("resume_match"))
async def resume_match(msg: Message):
    data = load_team_data()
    chat_id = str(msg.chat.id)

    if chat_id not in data:
        return await msg.answer("❌ No active match.")

    match = data[chat_id]
    if msg.from_user.id != match["referee"]:
        return await msg.answer("❌ Only referee can resume the match.")

    if not match["match_paused"]:
        return await msg.answer("⚠️ Match is not paused.")

    match["match_paused"] = False
    match["start_time"] = time.time()
    save_team_data(data)

    await msg.answer(f"▶️ Match resumed!\n⏱️ Time left: {format_time(match['time_left'])}")

# ✅ TEAM MODE: Scoreboard (30 sec cooldown)
@router.message(Command("score"))
async def score(msg: Message):
    if not cooldown_check(msg.chat.id, "score", 30):
        return await msg.answer("⏳ Please wait 30s before checking score again.")

    data = load_team_data()
    chat_id = str(msg.chat.id)
    if chat_id not in data:
        return await msg.answer("❌ No active match.")

    match = data[chat_id]
    set_cooldown(msg.chat.id, "score")

    await msg.answer(
        f"📊 SCOREBOARD\n\n"
        f"🏅 Team A: {match['score_a']}\n"
        f"🏅 Team B: {match['score_b']}\n"
        f"⏱️ Time left: {format_time(match['time_left'])}"
    )
