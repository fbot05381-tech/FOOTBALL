import random
import asyncio
import json
import os
from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from utils.db import load_json, save_json

router = Router()
DATA_DIR = "database"
TEAMS_FILE = os.path.join(DATA_DIR, "teams.json")
MATCH_FILE = os.path.join(DATA_DIR, "matches.json")
GIF_FILE = os.path.join(DATA_DIR, "gif_links.json")

def get_gif(key):
    gifs = load_json(GIF_FILE).get(key, [])
    return random.choice(gifs) if gifs else None

# 🎮 Start Match
@router.message(commands=["start_match"])
async def start_match(msg: Message):
    teams = load_json(TEAMS_FILE)
    if msg.from_user.id != teams.get("referee"):
        return await msg.answer("Only Referee can start the match.")

    if len(teams["team_a"]) < 1 or len(teams["team_b"]) < 1:
        return await msg.answer("Both teams must have players.")

    # Setup match state
    match = {
        "round": 1,
        "ball_possession": None,
        "score": {"A": 0, "B": 0}
    }
    save_json(MATCH_FILE, match)

    await msg.answer("🏁 Match starting in 3 rounds of 15 minutes each!")
    await countdown(msg)

    # Toss - captains DM me
    await toss_coin(msg, teams)

async def countdown(msg: Message):
    for i in ["3️⃣", "2️⃣", "1️⃣", "🏆"]:
        await msg.answer(f"Match starts in {i}")
        await asyncio.sleep(1)

async def toss_coin(msg: Message, teams):
    cap_a = list(teams["captains"].keys())[0]
    cap_b = list(teams["captains"].keys())[1]

    toss_result = random.choice(["head", "tail"])
    await msg.answer(f"Toss happening... Result: <b>{toss_result.upper()}</b>")

    # Randomly give ball to one team
    winner_team = random.choice(["A", "B"])
    match = load_json(MATCH_FILE)
    match["ball_possession"] = winner_team
    save_json(MATCH_FILE, match)

    await msg.answer(f"🎉 Team {winner_team} gets the ball first!")
    await next_turn(msg)

async def next_turn(msg: Message):
    match = load_json(MATCH_FILE)
    team = match["ball_possession"]
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚽ Kick", callback_data="action_kick")],
        [InlineKeyboardButton(text="🛡️ Defensive", callback_data="action_defensive")],
        [InlineKeyboardButton(text="🤝 Pass", callback_data="action_pass")]
    ])
    await msg.answer(f"Team {team} has the ball!\nChoose your move:", reply_markup=kb)

# ⚽ Kick
@router.callback_query(lambda c: c.data == "action_kick")
async def action_kick(cb):
    gif = get_gif("kick")
    match = load_json(MATCH_FILE)
    team = match["ball_possession"]

    await cb.message.answer("⚽ Attempting a GOAL!")
    if gif: await cb.message.answer_animation(gif)

    # Penalty shoot logic
    gk_team = "A" if team == "B" else "B"
    await cb.message.answer(f"Goalkeeper of Team {gk_team}, choose a number 1-5!\nShooter choose as well!")

    # Random result (simulate penalty)
    shooter_num = random.randint(1,5)
    gk_num = random.randint(1,5)

    await asyncio.sleep(2)
    if shooter_num != gk_num:
        match["score"][team] += 1
        await cb.message.answer(f"🥅 GOAL for Team {team}! Score: {match['score']['A']} - {match['score']['B']}")
    else:
        await cb.message.answer(f"🧤 SAVED by Team {gk_team}'s Goalkeeper!")

    save_json(MATCH_FILE, match)
    match["ball_possession"] = gk_team  # possession change
    save_json(MATCH_FILE, match)
    await next_turn(cb.message)

# 🛡️ Defensive
@router.callback_query(lambda c: c.data == "action_defensive")
async def action_defensive(cb):
    gif = get_gif("defensive")
    match = load_json(MATCH_FILE)
    team = match["ball_possession"]

    await cb.message.answer(f"🛡️ Team {team} is moving defensively!")
    if gif: await cb.message.answer_animation(gif)

    # Chance of ball steal
    if random.choice([True, False]):
        match["ball_possession"] = "A" if team == "B" else "B"
        await cb.message.answer("😱 Ball stolen by opposite team!")
    else:
        await cb.message.answer("✅ Ball kept safely!")

    save_json(MATCH_FILE, match)
    await next_turn(cb.message)

# 🤝 Pass
@router.callback_query(lambda c: c.data == "action_pass")
async def action_pass(cb):
    gif = get_gif("pass")
    match = load_json(MATCH_FILE)
    team = match["ball_possession"]

    await cb.message.answer(f"🤝 Team {team} is passing the ball!")
    if gif: await cb.message.answer_animation(gif)

    # Chance of interception
    if random.choice([True, False]):
        match["ball_possession"] = "A" if team == "B" else "B"
        await cb.message.answer("🚨 Opponent intercepted the pass!")
    else:
        await cb.message.answer("✅ Successful pass!")

    save_json(MATCH_FILE, match)
    await next_turn(cb.message)
