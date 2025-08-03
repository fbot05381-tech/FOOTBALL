import asyncio
import random
import time
from aiogram import Router, types
from aiogram.filters import Command

router = Router()

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

# ===== Helper =====
async def update_tournament_scoreboard(message: types.Message):
    if not tournament_data["score"]:
        return await message.answer("⚠️ No scores yet!")
    table = "🏆 <b>Tournament Scoreboard</b>\n\n"
    for team, score in tournament_data["score"].items():
        table += f"{team}: {score}\n"
    await message.answer(table)

async def create_tournament_from_button(chat_id, referee_id):
    from main import bot
    tournament_data["teams"].clear()
    tournament_data["referee"] = referee_id
    tournament_data["started"] = False
    tournament_data["paused"] = False
    await bot.send_message(chat_id, "✅ Tournament Created!\nPlayers join with /join_tournament")

# ===== Commands =====
@router.message(Command("create_tournament"))
async def create_tournament(message: types.Message):
    tournament_data["teams"].clear()
    tournament_data["referee"] = message.from_user.id
    tournament_data["started"] = False
    await message.answer("✅ Tournament Created!\nPlayers join with /join_tournament")

@router.message(Command("join_tournament"))
async def join_tournament(message: types.Message):
    uid = message.from_user.id
    name = message.from_user.full_name
    if any(uid in team for team in tournament_data["teams"].values()):
        return await message.answer("⚠️ Already in a team!")

    if not tournament_data["teams"]:
        tournament_data["teams"]["Team A"] = [uid]
        team = "Team A"
    else:
        if len(tournament_data["teams"].get("Team A", [])) <= len(tournament_data["teams"].get("Team B", [])):
            tournament_data["teams"].setdefault("Team A", []).append(uid)
            team = "Team A"
        else:
            tournament_data["teams"].setdefault("Team B", []).append(uid)
            team = "Team B"

    if team not in tournament_data["score"]:
        tournament_data["score"][team] = 0
    await message.answer(f"✅ {name} joined {team}!")

@router.message(Command("set_referee"))
async def set_referee(message: types.Message):
    tournament_data["referee"] = message.from_user.id
    await message.answer(f"👨‍⚖️ Referee set: {message.from_user.full_name}")

@router.message(Command("start_tournament"))
async def start_tournament(message: types.Message):
    if message.from_user.id != tournament_data["referee"]:
        return await message.answer("⚠️ Only referee can start!")
    tournament_data["started"] = True
    tournament_data["start_time"] = time.time()
    await message.answer("🎮 Tournament Started!")

@router.message(Command("end_tournament"))
async def end_tournament(message: types.Message):
    if message.from_user.id != tournament_data["referee"]:
        return await message.answer("⚠️ Only referee can end!")
    tournament_data["teams"].clear()
    tournament_data["score"].clear()
    await message.answer("🏁 Tournament Ended!")
