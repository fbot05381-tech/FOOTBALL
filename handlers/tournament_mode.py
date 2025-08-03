import random, asyncio
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from utils.db import read_db, update_db

router = Router()

# ✅ Create Tournament
@router.message(Command("create_tournament"))
async def create_tournament(msg: Message):
    chat_id = str(msg.chat.id)
    db = read_db()

    if chat_id in db and "tournament" in db[chat_id]:
        await msg.answer("⚠️ A tournament is already active in this group!")
        return

    db[chat_id] = {
        "tournament": {
            "owner": msg.from_user.id,
            "teams": {},
            "points": {},
            "matches": [],
            "current": None,
            "moves": {}
        }
    }
    update_db(chat_id, db[chat_id])
    await msg.answer("🏆 Tournament Created!\nUse /register_team <TeamName> to add teams.")

# ✅ Register Team
@router.message(Command("register_team"))
async def register_team(msg: Message):
    chat_id = str(msg.chat.id)
    db = read_db()

    if chat_id not in db or "tournament" not in db[chat_id]:
        await msg.answer("❌ No active tournament. Use /create_tournament first.")
        return

    args = msg.text.split(maxsplit=1)
    if len(args) < 2:
        await msg.answer("⚠️ Usage: /register_team TeamName")
        return

    team_name = args[1].strip()
    if team_name in db[chat_id]["tournament"]["teams"]:
        await msg.answer("⚠️ This team is already registered!")
        return

    db[chat_id]["tournament"]["teams"][team_name] = []
    db[chat_id]["tournament"]["points"][team_name] = 0
    update_db(chat_id, db[chat_id])
    await msg.answer(f"✅ Team <b>{team_name}</b> registered!", parse_mode="HTML")

# ✅ Start Match Between Two Teams
@router.message(Command("start_tournament_match"))
async def start_tournament_match(msg: Message):
    chat_id = str(msg.chat.id)
    db = read_db()

    if chat_id not in db or "tournament" not in db[chat_id]:
        await msg.answer("❌ No tournament found.")
        return

    args = msg.text.split()
    if len(args) < 3:
        await msg.answer("⚠️ Usage: /start_tournament_match TeamA TeamB")
        return

    teamA, teamB = args[1], args[2]
    if teamA not in db[chat_id]["tournament"]["teams"] or teamB not in db[chat_id]["tournament"]["teams"]:
        await msg.answer("❌ Both teams must be registered!")
        return

    db[chat_id]["tournament"]["current"] = {"teamA": teamA, "teamB": teamB, "score": {teamA: 0, teamB: 0}, "moves": {}}
    update_db(chat_id, db[chat_id])

    await msg.answer(f"🏟️ Tournament Match Started:\n🔵 {teamA} vs 🔴 {teamB}\nUse /tour_action KICK/PASS/DEFENSIVE")

# ✅ Player Action
@router.message(Command("tour_action"))
async def tour_action(msg: Message):
    chat_id = str(msg.chat.id)
    db = read_db()

    if chat_id not in db or not db[chat_id]["tournament"].get("current"):
        await msg.answer("❌ No active match in tournament.")
        return

    args = msg.text.split()
    if len(args) < 2:
        await msg.answer("⚠️ Usage: /tour_action KICK/PASS/DEFENSIVE")
        return

    move = args[1].upper()
    user = msg.from_user.mention_html()

    # Track moves for MVP
    match_data = db[chat_id]["tournament"]["current"]
    if user not in match_data["moves"]:
        match_data["moves"][user] = 0
    match_data["moves"][user] += 1
    update_db(chat_id, db[chat_id])

    if move == "KICK":
        await msg.answer(f"⚽ {user} attempts a goal! Waiting for GK... (/tour_gk number)")
        return
    if move == "PASS":
        await msg.answer(f"🔄 {user} made a pass!")
        return
    if move == "DEFENSIVE":
        await msg.answer(f"🛡️ {user} is defending!")
        return

    await msg.answer("❌ Invalid move!")

# ✅ Goalkeeper Save (Penalty)
@router.message(Command("tour_gk"))
async def tour_gk(msg: Message):
    chat_id = str(msg.chat.id)
    db = read_db()

    if chat_id not in db or not db[chat_id]["tournament"].get("current"):
        await msg.answer("❌ No active match.")
        return

    args = msg.text.split()
    if len(args) < 2 or not args[1].isdigit():
        await msg.answer("⚠️ Usage: /tour_gk number(1-5)")
        return

    gk_num = int(args[1])
    player_num = random.randint(1, 5)
    match_data = db[chat_id]["tournament"]["current"]
    teamA, teamB = match_data["teamA"], match_data["teamB"]

    if gk_num == player_num:
        await msg.answer(f"🧤 Goal SAVED! Number was {player_num}")
    else:
        scoring_team = random.choice([teamA, teamB])
        match_data["score"][scoring_team] += 1
        await msg.answer(f"🥅 GOAL for <b>{scoring_team}</b>! Number was {player_num}", parse_mode="HTML")

    update_db(chat_id, db[chat_id])

# ✅ End Tournament Match
@router.message(Command("end_tournament_match"))
async def end_tournament_match(msg: Message):
    chat_id = str(msg.chat.id)
    db = read_db()

    if chat_id not in db or not db[chat_id]["tournament"].get("current"):
        await msg.answer("❌ No active tournament match.")
        return

    match_data = db[chat_id]["tournament"]["current"]
    teamA, teamB = match_data["teamA"], match_data["teamB"]
    scoreA, scoreB = match_data["score"][teamA], match_data["score"][teamB]

    if scoreA > scoreB:
        winner = teamA
        db[chat_id]["tournament"]["points"][teamA] += 3
    elif scoreB > scoreA:
        winner = teamB
        db[chat_id]["tournament"]["points"][teamB] += 3
    else:
        winner = "DRAW"
        db[chat_id]["tournament"]["points"][teamA] += 1
        db[chat_id]["tournament"]["points"][teamB] += 1

    # MVP
    if match_data["moves"]:
        mvp = max(match_data["moves"], key=match_data["moves"].get)
    else:
        mvp = "None"

    # Final Summary
    summary = f"🏆 <b>TOURNAMENT MATCH SUMMARY</b>\n\n{teamA}: {scoreA}\n{teamB}: {scoreB}\n\n🥇 Winner: {winner}\n⭐ MVP: {mvp}"
    await msg.answer(summary, parse_mode="HTML")

    # GIF
    gifs = [
        "https://media.giphy.com/media/3o6Zt481isNVuQI1l6/giphy.gif",
        "https://media.giphy.com/media/xT0xeJpnrWC4XWblEk/giphy.gif"
    ]
    await msg.answer_animation(random.choice(gifs))

    db[chat_id]["tournament"]["current"] = None
    update_db(chat_id, db[chat_id])

# ✅ Show Points Table
@router.message(Command("points_table"))
async def points_table(msg: Message):
    chat_id = str(msg.chat.id)
    db = read_db()

    if chat_id not in db or "tournament" not in db[chat_id]:
        await msg.answer("❌ No tournament found.")
        return

    points = db[chat_id]["tournament"]["points"]
    table = "📊 <b>TOURNAMENT POINTS TABLE</b>\n\n"
    for team, pts in sorted(points.items(), key=lambda x: x[1], reverse=True):
        table += f"🏅 {team}: {pts} points\n"

    await msg.answer(table, parse_mode="HTML")
