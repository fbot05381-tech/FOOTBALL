import asyncio
import random
import time
from aiogram import Router, types
from aiogram.filters import Command

router = Router()

tournament_data = {
    "teams": {"Team A": [], "Team B": []},
    "referee": None,
    "started": False,
    "paused": False,
    "score": {"Team A": 0, "Team B": 0},
    "stats": {},
    "captains": {},
    "goalkeepers": {},
    "start_time": None
}

join_phase_active = False
join_message_ids = []

tournament_score_cooldown = 0

# ====== Helper Functions ======
async def update_tournament_scoreboard(message: types.Message):
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

# ====== Join Phase ======
async def start_tournament_join_phase(message: types.Message):
    global join_phase_active, join_message_ids
    join_phase_active = True
    tournament_data["teams"]["Team A"].clear()
    tournament_data["teams"]["Team B"].clear()
    tournament_data["started"] = False
    tournament_data["paused"] = False
    join_message_ids = []

    msg_a = await message.answer("⏳ <b>Join Tournament Team A</b> using /join_tournamentA (2 min)")
    msg_b = await message.answer("⏳ <b>Join Tournament Team B</b> using /join_tournamentB (2 min)")
    join_message_ids.extend([msg_a.message_id, msg_b.message_id])

    # 2 min wait
    await asyncio.sleep(120)
    join_phase_active = False

    # Delete join messages
    for mid in join_message_ids:
        try:
            await message.chat.delete_message(mid)
        except:
            pass

    await message.answer("⏳ Join phase ended! Referee can now balance teams and use /start_tournament")

# ====== Commands ======
@router.message(Command("create_tournament"))
async def create_tournament(message: types.Message):
    tournament_data["referee"] = message.from_user.id
    tournament_data["started"] = False
    tournament_data["paused"] = False
    tournament_data["score"] = {"Team A": 0, "Team B": 0}
    tournament_data["stats"].clear()
    await message.answer("✅ Tournament Created!\n⏳ Starting join phase for 2 minutes...")
    await start_tournament_join_phase(message)

@router.message(Command("join_tournamentA"))
async def join_tournament_a(message: types.Message):
    if not join_phase_active:
        return await message.answer("⚠️ Join phase is over or not started!")
    uid = message.from_user.id
    if uid in tournament_data["teams"]["Team A"] or uid in tournament_data["teams"]["Team B"]:
        return await message.answer("⚠️ Already joined a team!")
    tournament_data["teams"]["Team A"].append(uid)
    await message.answer(f"✅ {message.from_user.full_name} joined Team A!")

@router.message(Command("join_tournamentB"))
async def join_tournament_b(message: types.Message):
    if not join_phase_active:
        return await message.answer("⚠️ Join phase is over or not started!")
    uid = message.from_user.id
    if uid in tournament_data["teams"]["Team A"] or uid in tournament_data["teams"]["Team B"]:
        return await message.answer("⚠️ Already joined a team!")
    tournament_data["teams"]["Team B"].append(uid)
    await message.answer(f"✅ {message.from_user.full_name} joined Team B!")

@router.message(Command("set_referee"))
async def set_referee(message: types.Message):
    tournament_data["referee"] = message.from_user.id
    await message.answer(f"👨‍⚖️ Referee set: {message.from_user.full_name}")

@router.message(Command("start_tournament"))
async def start_tournament(message: types.Message):
    if message.from_user.id != tournament_data["referee"]:
        return await message.answer("⚠️ Only referee can start the tournament!")
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
    tournament_data["teams"]["Team A"].clear()
    tournament_data["teams"]["Team B"].clear()
    tournament_data["stats"].clear()
    tournament_data["score"] = {"Team A": 0, "Team B": 0}
    tournament_data["paused"] = False
    tournament_data["started"] = False
