import asyncio
import random
import time
from aiogram import Router, types
from aiogram.filters import Command

router = Router()

# ====== Tournament Data ======
tournament_data = {
    "teams": {},
    "referee": None,
    "started": False,
    "paused": False,
    "score": {},
    "stats": {},
    "captains": {},
    "goalkeepers": {},
    "start_time": None
}

tournament_score_cooldown = 0

# ====== Helper Functions ======
async def update_tournament_scoreboard(message: types.Message):
    if not tournament_data["score"]:
        return await message.answer("⚠️ No scores yet!")
    table = "🏆 <b>Tournament Scoreboard</b>\n\n"
    for team, score in tournament_data["score"].items():
        table += f"{team}: {score}\n"
    await message.answer(table)

async def auto_mvp_tournament():
    best = None
    max_score = 0
    for player, stats in tournament_data["stats"].items():
        score = stats.get("goals", 0) * 2 + stats.get("assists", 0)
        if score > max_score:
            max_score = score
            best = player
    return best or "No MVP"

# ====== Commands ======

@router.message(Command("create_tournament"))
async def create_tournament(message: types.Message):
    tournament_data["teams"].clear()
    tournament_data["referee"] = message.from_user.id
    tournament_data["started"] = False
    tournament_data["paused"] = False
    tournament_data["score"].clear()
    tournament_data["stats"].clear()
    await message.answer(
        "✅ Tournament Created!\n"
        "Players join with:\n"
        "/join_tournament\n\n"
        "👨‍⚖️ Referee: You"
    )

@router.message(Command("set_referee"))
async def set_referee(message: types.Message):
    if message.reply_to_message:
        ref_id = message.reply_to_message.from_user.id
        ref_name = message.reply_to_message.from_user.full_name
    else:
        ref_id = message.from_user.id
        ref_name = message.from_user.full_name

    tournament_data["referee"] = ref_id
    await message.answer(f"👨‍⚖️ Referee set: {ref_name}")

@router.message(Command("get_referee"))
async def get_referee(message: types.Message):
    ref = tournament_data["referee"]
    if not ref:
        return await message.answer("⚠️ No referee set yet!")
    await message.answer(f"👨‍⚖️ Current Referee ID: <code>{ref}</code>")

@router.message(Command("join_tournament"))
async def join_tournament(message: types.Message):
    user = message.from_user.full_name
    uid = message.from_user.id

    # पहले से किसी टीम में है?
    for members in tournament_data["teams"].values():
        if uid in members:
            return await message.answer("⚠️ Already in a team!")

    # Auto assign to Team A or B
    if not tournament_data["teams"]:
        tournament_data["teams"]["Team A"] = [uid]
        team = "Team A"
    else:
        team_a = len(tournament_data["teams"].get("Team A", []))
        team_b = len(tournament_data["teams"].get("Team B", []))
        if team_a <= team_b:
            tournament_data["teams"].setdefault("Team A", []).append(uid)
            team = "Team A"
        else:
            tournament_data["teams"].setdefault("Team B", []).append(uid)
            team = "Team B"

    # Score init
    if team not in tournament_data["score"]:
        tournament_data["score"][team] = 0

    await message.answer(f"✅ {user} joined {team}!")

@router.message(Command("start_tournament"))
async def start_tournament(message: types.Message):
    if message.from_user.id != tournament_data["referee"]:
        return await message.answer("⚠️ Only referee can start the tournament!")

    if not tournament_data["teams"]:
        return await message.answer("⚠️ No teams joined yet!")

    tournament_data["started"] = True
    tournament_data["start_time"] = time.time()
    await message.answer("🎮 Tournament Started!")

@router.message(Command("pause_tournament"))
async def pause_tournament(message: types.Message):
    if message.from_user.id != tournament_data["referee"]:
        return await message.answer("⚠️ Only referee can pause!")

    tournament_data["paused"] = True
    await message.answer("⏸️ Tournament Paused! (Pinned)")
    await message.pin()

@router.message(Command("resume_tournament"))
async def resume_tournament(message: types.Message):
    if message.from_user.id != tournament_data["referee"]:
        return await message.answer("⚠️ Only referee can resume!")

    tournament_data["paused"] = False
    await message.answer("▶️ Tournament Resumed!")

@router.message(Command("score"))
async def tournament_score(message: types.Message):
    global tournament_score_cooldown
    now = time.time()
    if now - tournament_score_cooldown < 30:
        return await message.answer("⏳ Please wait before using /score again!")
    tournament_score_cooldown = now
    await update_tournament_scoreboard(message)

@router.message(Command("end_tournament"))
async def end_tournament(message: types.Message):
    if message.from_user.id != tournament_data["referee"]:
        return await message.answer("⚠️ Only referee can end tournament!")

    mvp = await auto_mvp_tournament()
    await message.answer(f"🏁 Tournament Ended!\nMVP: {mvp}")

    # Reset Data
    tournament_data["teams"].clear()
    tournament_data["stats"].clear()
    tournament_data["score"].clear()
    tournament_data["paused"] = False
    tournament_data["started"] = False
