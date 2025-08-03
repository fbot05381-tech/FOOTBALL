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
    "ball_holder": None,
    "join_open": False
}

score_cooldown = 0
command_cooldowns = {}
JOIN_DURATION = 120  # 2 minutes

# ===== Helper Functions =====
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
    return best or "No MVP"

# ===== Commands =====

@router.message(Command("create_match"))
async def create_match(message: types.Message):
    if match_data["join_open"]:
        return await message.answer("⚠️ Joining is already in progress!")

    match_data["team_a"].clear()
    match_data["team_b"].clear()
    match_data["score"] = {"A": 0, "B": 0}
    match_data["stats"].clear()
    match_data["started"] = False
    match_data["paused"] = False
    match_data["referee"] = message.from_user.id
    match_data["join_open"] = True

    msgA = await message.answer("🔵 Join Team A (2 min): /join_teamA")
    msgB = await message.answer("🔴 Join Team B (2 min): /join_teamB")

    # 2-minute timer to close joining
    async def close_joining():
        await asyncio.sleep(JOIN_DURATION)
        match_data["join_open"] = False
        try:
            await msgA.delete()
            await msgB.delete()
        except:
            pass
        await message.answer("⏳ Joining closed! Referee can now /start_match")

    asyncio.create_task(close_joining())

@router.message(Command("join_teamA"))
async def join_team_a(message: types.Message):
    if not match_data["join_open"]:
        return await message.answer("⚠️ Joining is closed!")
    if message.from_user.id in match_data["team_a"] or message.from_user.id in match_data["team_b"]:
        return await message.answer("⚠️ Already joined!")
    match_data["team_a"].append(message.from_user.id)
    await message.answer(f"✅ {message.from_user.full_name} joined Team A")

@router.message(Command("join_teamB"))
async def join_team_b(message: types.Message):
    if not match_data["join_open"]:
        return await message.answer("⚠️ Joining is closed!")
    if message.from_user.id in match_data["team_a"] or message.from_user.id in match_data["team_b"]:
        return await message.answer("⚠️ Already joined!")
    match_data["team_b"].append(message.from_user.id)
    await message.answer(f"✅ {message.from_user.full_name} joined Team B")

@router.message(Command("set_referee"))
async def set_referee(message: types.Message):
    if message.reply_to_message:
        ref_id = message.reply_to_message.from_user.id
        ref_name = message.reply_to_message.from_user.full_name
    else:
        ref_id = message.from_user.id
        ref_name = message.from_user.full_name
    match_data["referee"] = ref_id
    await message.answer(f"👨‍⚖️ Referee set: {ref_name}")

@router.message(Command("get_referee"))
async def get_referee(message: types.Message):
    ref = match_data["referee"]
    if not ref:
        return await message.answer("⚠️ No referee set!")
    await message.answer(f"👨‍⚖️ Current Referee ID: <code>{ref}</code>")

@router.message(Command("start_match"))
async def start_match(message: types.Message):
    if message.from_user.id != match_data["referee"]:
        return await message.answer("⚠️ Only referee can start the match!")
    match_data["started"] = True
    match_data["start_time"] = time.time()
    if match_data["team_a"] and match_data["team_b"]:
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
        return await message.answer("⏳ Please wait!")
    score_cooldown = now
    await update_scoreboard(message)

@router.message(Command("end_match"))
async def end_match(message: types.Message):
    if message.from_user.id != match_data["referee"]:
        return await message.answer("⚠️ Only referee can end the match!")
    mvp = await auto_mvp()
    await message.answer(f"🏁 Match Ended!\nMVP: {mvp}")
    match_data.update({
        "team_a": [], "team_b": [], "referee": None,
        "started": False, "paused": False,
        "score": {"A": 0, "B": 0}, "stats": {},
        "ball_holder": None, "join_open": False
    })
