import asyncio
import random
import time
from aiogram import Router, types
from aiogram.filters import Command

router = Router()

# ====== Match Data ======
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
    "join_phase": False
}

score_cooldown = 0
command_cooldowns = {}
join_messages = []

# ====== Helper Functions ======
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

def can_use_command(uid):
    now = time.time()
    if uid not in command_cooldowns:
        command_cooldowns[uid] = now
        return True
    if now - command_cooldowns[uid] >= 10:
        command_cooldowns[uid] = now
        return True
    return False

# ====== Commands ======

@router.message(Command("create_match"))
async def create_match(message: types.Message):
    match_data["team_a"].clear()
    match_data["team_b"].clear()
    match_data["score"] = {"A": 0, "B": 0}
    match_data["stats"].clear()
    match_data["started"] = False
    match_data["paused"] = False
    match_data["ball_holder"] = None
    match_data["referee"] = message.from_user.id
    match_data["join_phase"] = True

    msg_a = await message.answer("⏳ Players join Team A using /join_teamA (2 min)")
    msg_b = await message.answer("⏳ Players join Team B using /join_teamB (2 min)")
    join_messages.extend([msg_a.message_id, msg_b.message_id])

    # 2 minute join window
    await asyncio.sleep(120)
    match_data["join_phase"] = False
    try:
        await message.bot.delete_message(message.chat.id, msg_a.message_id)
        await message.bot.delete_message(message.chat.id, msg_b.message_id)
    except:
        pass

    await message.answer("✅ Join time ended! Referee can now balance teams and start the match with /start_match")

@router.message(Command("join_teamA"))
async def join_team_a(message: types.Message):
    if not match_data["join_phase"]:
        return await message.answer("⚠️ Joining is closed!")
    uid = message.from_user.id
    if uid in match_data["team_a"] or uid in match_data["team_b"]:
        return await message.answer("⚠️ Already in a team!")
    match_data["team_a"].append(uid)
    await message.answer(f"✅ {message.from_user.full_name} joined Team A!")

@router.message(Command("join_teamB"))
async def join_team_b(message: types.Message):
    if not match_data["join_phase"]:
        return await message.answer("⚠️ Joining is closed!")
    uid = message.from_user.id
    if uid in match_data["team_a"] or uid in match_data["team_b"]:
        return await message.answer("⚠️ Already in a team!")
    match_data["team_b"].append(uid)
    await message.answer(f"✅ {message.from_user.full_name} joined Team B!")

@router.message(Command("set_referee"))
async def set_referee(message: types.Message):
    if message.reply_to_message:
        match_data["referee"] = message.reply_to_message.from_user.id
        name = message.reply_to_message.from_user.full_name
    else:
        match_data["referee"] = message.from_user.id
        name = message.from_user.full_name
    await message.answer(f"👨‍⚖️ Referee set: {name}")

@router.message(Command("start_match"))
async def start_match(message: types.Message):
    if message.from_user.id != match_data["referee"]:
        return await message.answer("⚠️ Only referee can start the match!")

    if not match_data["team_a"] or not match_data["team_b"]:
        return await message.answer("⚠️ Both teams need players!")

    match_data["started"] = True
    match_data["start_time"] = time.time()
    all_players = match_data["team_a"] + match_data["team_b"]
    match_data["ball_holder"] = random.choice(all_players) if all_players else None
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
    match_data["team_a"].clear()
    match_data["team_b"].clear()
    match_data["stats"].clear()
    match_data["score"] = {"A": 0, "B": 0}
    match_data["started"] = False
    match_data["paused"] = False
    match_data["ball_holder"] = None
    match_data["join_phase"] = False
