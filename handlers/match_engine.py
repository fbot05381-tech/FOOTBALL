import os
import random
import asyncio
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from utils.db import load_json, save_json

router = Router()
DATA_DIR = "database"
TEAMS_FILE = os.path.join(DATA_DIR, "teams.json")
MATCH_FILE = os.path.join(DATA_DIR, "matches.json")

@router.message(Command("start_match"))
async def start_match(msg: types.Message):
    teams = load_json(TEAMS_FILE)
    if msg.from_user.id != teams.get("referee"):
        return await msg.answer("Only Referee can start the match.")
    if len(teams["team_a"]) < 1 or len(teams["team_b"]) < 1:
        return await msg.answer("Both teams must have players.")

    match = {"round": 1, "ball_possession": None, "score": {"A": 0, "B": 0}}
    save_json(MATCH_FILE, match)

    await msg.answer("🏁 Match starting in 3 rounds of 15 minutes each!")
    for i in ["3️⃣", "2️⃣", "1️⃣", "🏆"]:
        await msg.answer(f"Match starts in {i}")
        await asyncio.sleep(1)

    toss_result = random.choice(["A", "B"])
    match["ball_possession"] = toss_result
    save_json(MATCH_FILE, match)
    await msg.answer(f"🎲 Toss complete! Team {toss_result} gets the ball first!")
    await next_turn(msg)

async def next_turn(msg: types.Message):
    match = load_json(MATCH_FILE)
    team = match["ball_possession"]
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚽ Kick", callback_data="action_kick")],
        [InlineKeyboardButton(text="🛡️ Defensive", callback_data="action_defensive")],
        [InlineKeyboardButton(text="🤝 Pass", callback_data="action_pass")]
    ])
    await msg.answer(f"Team {team} has the ball!\nChoose your move:", reply_markup=kb)

@router.callback_query(F.data == "action_kick")
async def action_kick(cb: CallbackQuery):
    match = load_json(MATCH_FILE)
    teams = load_json(TEAMS_FILE)
    team = match["ball_possession"]
    gk_team = "A" if team == "B" else "B"

    shooter_num = random.randint(1,5)

    # ✅ Goalkeeper check
    gk_id = teams.get(f"gk_{gk_team}")
    gk_num = random.randint(1,5)

    if shooter_num != gk_num:
        match["score"][team] += 1
        await cb.message.answer(f"🥅 GOAL for Team {team}! Score: {match['score']['A']} - {match['score']['B']}")
    else:
        await cb.message.answer(f"🧤 SAVED by Team {gk_team}'s Goalkeeper!")

    match["ball_possession"] = gk_team
    save_json(MATCH_FILE, match)
    await next_turn(cb.message)

@router.callback_query(F.data == "action_defensive")
async def action_defensive(cb: CallbackQuery):
    match = load_json(MATCH_FILE)
    team = match["ball_possession"]
    if random.choice([True, False]):
        match["ball_possession"] = "A" if team == "B" else "B"
        await cb.message.answer("😱 Ball stolen by opposite team!")
    else:
        await cb.message.answer(f"🛡️ Team {team} kept the ball safely!")
    save_json(MATCH_FILE, match)
    await next_turn(cb.message)

@router.callback_query(F.data == "action_pass")
async def action_pass(cb: CallbackQuery):
    match = load_json(MATCH_FILE)
    team = match["ball_possession"]
    if random.choice([True, False]):
        match["ball_possession"] = "A" if team == "B" else "B"
        await cb.message.answer("🚨 Opponent intercepted the pass!")
    else:
        await cb.message.answer(f"🤝 Team {team} passed successfully!")
    save_json(MATCH_FILE, match)
    await next_turn(cb.message)

# ✅ END MATCH COMMAND
@router.message(Command("end_match"))
async def end_match(msg: types.Message):
    teams = load_json(TEAMS_FILE)
    if msg.from_user.id != teams.get("referee"):
        return await msg.answer("Only Referee can end the match.")
    
    match = load_json(MATCH_FILE)
    score_a = match["score"]["A"]
    score_b = match["score"]["B"]

    if score_a > score_b:
        winner = "Team A"
    elif score_b > score_a:
        winner = "Team B"
    else:
        winner = "DRAW"

    await msg.answer(f"🏁 Match Ended!\n\nFinal Score:\nTeam A {score_a} - {score_b} Team B\n🏆 Winner: {winner}")
