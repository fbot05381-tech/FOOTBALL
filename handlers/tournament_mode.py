import asyncio
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
    "start_time": None,
    "join_open": False
}

JOIN_DURATION = 120  # 2 min join

async def update_tournament_scoreboard(message: types.Message):
    if not tournament_data["score"]:
        return await message.answer("⚠️ No scores yet!")
    table = "🏆 <b>Tournament Scoreboard</b>\n\n"
    for team, score in tournament_data["score"].items():
        table += f"{team}: {score}\n"
    await message.answer(table)

@router.message(Command("create_tournament"))
async def create_tournament(message: types.Message):
    tournament_data["teams"].clear()
    tournament_data["score"].clear()
    tournament_data["stats"].clear()
    tournament_data["referee"] = message.from_user.id
    tournament_data["join_open"] = True

    msg = await message.answer("🏆 Tournament Created!\nUse /join_tournament to join (2 min)")

    async def close_joining():
        await asyncio.sleep(JOIN_DURATION)
        tournament_data["join_open"] = False
        try:
            await msg.delete()
        except:
            pass
        await message.answer("⏳ Joining closed! Referee can now /start_tournament")

    asyncio.create_task(close_joining())

@router.message(Command("join_tournament"))
async def join_tournament(message: types.Message):
    if not tournament_data["join_open"]:
        return await message.answer("⚠️ Joining closed!")
    uid = message.from_user.id
    if any(uid in t for t in tournament_data["teams"].values()):
        return await message.answer("⚠️ Already in a team!")
    if not tournament_data["teams"]:
        tournament_data["teams"]["Team A"] = [uid]
        team = "Team A"
    else:
        a = len(tournament_data["teams"].get("Team A", []))
        b = len(tournament_data["teams"].get("Team B", []))
        if a <= b:
            tournament_data["teams"].setdefault("Team A", []).append(uid)
            team = "Team A"
        else:
            tournament_data["teams"].setdefault("Team B", []).append(uid)
            team = "Team B"
    tournament_data["score"].setdefault(team, 0)
    await message.answer(f"✅ {message.from_user.full_name} joined {team}!")

@router.message(Command("set_referee"))
async def set_referee(message: types.Message):
    ref_id = message.from_user.id
    tournament_data["referee"] = ref_id
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
    await message.answer("🏁 Tournament Ended!")
    tournament_data.update({
        "teams": {}, "score": {}, "stats": {},
        "referee": None, "started": False, "paused": False,
        "join_open": False
    })
