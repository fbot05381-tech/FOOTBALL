import asyncio
import random
import datetime
from aiogram import Router, types
from aiogram.filters import Command
from utils.db import read_json, write_json, MATCH_DB, PLAYER_DB

router = Router()

MATCH_STATE = {
    "is_running": False,
    "paused": False,
    "start_time": None,
    "time_left": 15 * 60,
    "team_a": [],
    "team_b": [],
    "score_a": 0,
    "score_b": 0,
    "referee": None,
    "events": []
}

# ✅ /start_match
@router.message(Command("start_match"))
async def start_match(msg: types.Message):
    if MATCH_STATE["is_running"]:
        await msg.answer("⚠️ Match already running!")
        return
    MATCH_STATE["is_running"] = True
    MATCH_STATE["paused"] = False
    MATCH_STATE["start_time"] = datetime.datetime.utcnow()
    MATCH_STATE["score_a"] = 0
    MATCH_STATE["score_b"] = 0
    MATCH_STATE["events"] = []
    await msg.answer("✅ Match Started! Use /pause_game to pause.")

# ✅ /pause_game
@router.message(Command("pause_game"))
async def pause_game(msg: types.Message):
    if not MATCH_STATE["is_running"]:
        await msg.answer("⚠️ No match running.")
        return
    MATCH_STATE["paused"] = True
    await msg.answer("⏸ Match Paused.")

# ✅ /resume_game
@router.message(Command("resume_game"))
async def resume_game(msg: types.Message):
    if not MATCH_STATE["is_running"]:
        await msg.answer("⚠️ No match running.")
        return
    MATCH_STATE["paused"] = False
    await msg.answer("▶ Match Resumed.")

# ✅ /end_match
@router.message(Command("end_match"))
async def end_match(msg: types.Message):
    if not MATCH_STATE["is_running"]:
        await msg.answer("⚠️ No match running.")
        return
    MATCH_STATE["is_running"] = False
    await msg.answer(f"🏁 Match Ended!\n\nFinal Score:\nA {MATCH_STATE['score_a']} - {MATCH_STATE['score_b']} B")

# ✅ /score (30 sec cooldown)
last_score_call = {}

@router.message(Command("score"))
async def score_cmd(msg: types.Message):
    now = datetime.datetime.utcnow()
    if msg.chat.id in last_score_call:
        diff = (now - last_score_call[msg.chat.id]).total_seconds()
        if diff < 30:
            await msg.answer(f"⏳ Wait {int(30 - diff)}s before using /score again.")
            return
    last_score_call[msg.chat.id] = now
    await msg.answer(f"📊 Current Score:\nA {MATCH_STATE['score_a']} - {MATCH_STATE['score_b']} B")

# ✅ /time (real-time + GIF combo)
@router.message(Command("time"))
async def time_cmd(msg: types.Message):
    left = MATCH_STATE["time_left"] // 60
    await msg.answer(f"⏱ Time Left: {left} min", parse_mode="HTML")
