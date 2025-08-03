import asyncio
import time
import json
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from utils.db import load_tournament_data, save_tournament_data
from utils.helpers import cooldown_check, set_cooldown, format_time

router = Router()

# ✅ Create Tournament
@router.message(Command("create_tournament"))
async def create_tournament(msg: Message):
    data = load_tournament_data()
    chat_id = str(msg.chat.id)

    data[chat_id] = {
        "referee": msg.from_user.id,
        "teams": {},
        "scores": {},
        "match_paused": False,
        "paused_at": None,
        "time_left": 20 * 60,
        "start_time": None,
        "cooldowns": {}
    }
    save_tournament_data(data)
    await msg.answer("🏆 Tournament created!\nUse /start_tournament to begin.")

# ✅ Start Tournament
@router.message(Command("start_tournament"))
async def start_tournament(msg: Message):
    data = load_tournament_data()
    chat_id = str(msg.chat.id)

    if chat_id not in data:
        return await msg.answer("❌ No tournament found.")

    if msg.from_user.id != data[chat_id]["referee"]:
        return await msg.answer("❌ Only referee can start the tournament.")

    data[chat_id]["start_time"] = time.time()
    save_tournament_data(data)
    await msg.answer("🏁 Tournament started!\nUse /pause_tournament to pause.")

# ✅ Pause Tournament
@router.message(Command("pause_tournament"))
async def pause_tournament(msg: Message):
    data = load_tournament_data()
    chat_id = str(msg.chat.id)

    if chat_id not in data:
        return await msg.answer("❌ No active tournament.")

    match = data[chat_id]
    if msg.from_user.id != match["referee"]:
        return await msg.answer("❌ Only referee can pause the tournament.")

    if match["match_paused"]:
        return await msg.answer("⚠️ Tournament is already paused.")

    elapsed = time.time() - match["start_time"]
    match["time_left"] -= elapsed
    match["match_paused"] = True
    match["paused_at"] = time.time()
    save_tournament_data(data)

    await msg.answer(f"⏸️ Tournament paused!\n⏱️ Time left: {format_time(match['time_left'])}")

# ✅ Resume Tournament
@router.message(Command("resume_tournament"))
async def resume_tournament(msg: Message):
    data = load_tournament_data()
    chat_id = str(msg.chat.id)

    if chat_id not in data:
        return await msg.answer("❌ No active tournament.")

    match = data[chat_id]
    if msg.from_user.id != match["referee"]:
        return await msg.answer("❌ Only referee can resume the tournament.")

    if not match["match_paused"]:
        return await msg.answer("⚠️ Tournament is not paused.")

    match["match_paused"] = False
    match["start_time"] = time.time()
    save_tournament_data(data)

    await msg.answer(f"▶️ Tournament resumed!\n⏱️ Time left: {format_time(match['time_left'])}")

# ✅ End Tournament (Referee only)
@router.message(Command("end_tournament"))
async def end_tournament(msg: Message):
    data = load_tournament_data()
    chat_id = str(msg.chat.id)

    if chat_id not in data:
        return await msg.answer("❌ No active tournament.")

    if msg.from_user.id != data[chat_id]["referee"]:
        return await msg.answer("❌ Only referee can end the tournament.")

    del data[chat_id]
    save_tournament_data(data)
    await msg.answer("🏆 Tournament ended!")

# ✅ Tournament Scoreboard (30 sec cooldown)
@router.message(Command("t_score"))
async def tournament_score(msg: Message):
    if not cooldown_check(msg.chat.id, "t_score", 30):
        return await msg.answer("⏳ Please wait 30s before checking tournament score again.")

    data = load_tournament_data()
    chat_id = str(msg.chat.id)
    if chat_id not in data:
        return await msg.answer("❌ No active tournament.")

    match = data[chat_id]
    set_cooldown(msg.chat.id, "t_score")

    score_text = "📊 TOURNAMENT SCOREBOARD\n\n"
    for team, score in match["scores"].items():
        score_text += f"🏅 {team}: {score}\n"

    score_text += f"\n⏱️ Time left: {format_time(match['time_left'])}"
    await msg.answer(score_text)
