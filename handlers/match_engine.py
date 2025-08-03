import random
from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from utils.db import read_db, update_db

router = Router()

# ✅ Start Match
@router.message(Command("start_match"))
async def start_match(msg: Message):
    chat_id = str(msg.chat.id)
    db = read_db()

    if chat_id not in db or "teamA" not in db[chat_id]:
        await msg.answer("❌ Teams are not created yet.")
        return

    if len(db[chat_id]["teamA"]) == 0 or len(db[chat_id]["teamB"]) == 0:
        await msg.answer("⚠️ Both teams must have players to start match!")
        return

    db[chat_id]["ball"] = None
    db[chat_id]["score"] = {"A": 0, "B": 0}
    update_db(chat_id, db[chat_id])

    await msg.answer("🏆 Match Started!\n⚽ Use /kickoff to decide who starts with the ball.")

# ✅ Kickoff (Head/Tail for Captains)
@router.message(Command("kickoff"))
async def kickoff(msg: Message):
    chat_id = str(msg.chat.id)
    db = read_db()

    if chat_id not in db or "teamA" not in db[chat_id]:
        await msg.answer("❌ Teams are not ready.")
        return

    if not db[chat_id]["captains"]:
        await msg.answer("⚠️ Captains must be set with /set_captain first!")
        return

    coin = random.choice(["head", "tail"])
    db[chat_id]["ball"] = "A" if coin == "head" else "B"
    update_db(chat_id, db[chat_id])

    await msg.answer(f"🪙 Coin Toss Result: <b>{coin.upper()}</b>\n⚽ Team {db[chat_id]['ball']} starts with the ball!", parse_mode="HTML")

# ✅ Player Action (KICK/PASS/DEFENSIVE)
@router.message(Command("action"))
async def action(msg: Message):
    chat_id = str(msg.chat.id)
    db = read_db()

    if chat_id not in db or "ball" not in db[chat_id]:
        await msg.answer("❌ Match not started.")
        return

    args = msg.text.split()
    if len(args) < 2:
        await msg.answer("⚠️ Usage: /action KICK or /action PASS or /action DEFENSIVE")
        return

    move = args[1].upper()
    ball_team = db[chat_id]["ball"]

    if move == "KICK":
        await msg.answer(f"⚽ Team {ball_team} attempts a GOAL!\n🧤 Waiting for Goalkeeper...")
        db[chat_id]["pending_kick"] = ball_team
        update_db(chat_id, db[chat_id])
        return

    if move == "PASS":
        await msg.answer(f"🔄 Team {ball_team} passed the ball to a teammate!")
        return

    if move == "DEFENSIVE":
        await msg.answer(f"🛡️ Team {ball_team} is playing defensive!")
        return

    await msg.answer("❌ Invalid move. Use KICK / PASS / DEFENSIVE.")

# ✅ Goalkeeper Save (Penalty Number System)
@router.message(Command("gk_save"))
async def gk_save(msg: Message):
    chat_id = str(msg.chat.id)
    db = read_db()

    if chat_id not in db or "pending_kick" not in db[chat_id]:
        await msg.answer("❌ No active goal attempt.")
        return

    args = msg.text.split()
    if len(args) < 2 or not args[1].isdigit():
        await msg.answer("⚠️ Usage: /gk_save number(1-5)")
        return

    player_guess = random.randint(1, 5)
    gk_guess = int(args[1])

    if player_guess == gk_guess:
        await msg.answer(f"🧤 Goalkeeper SAVED the goal! Number was {player_guess}.")
    else:
        scoring_team = db[chat_id]["pending_kick"]
        db[chat_id]["score"][scoring_team] += 1
        await msg.answer(f"🥅 GOAL for Team {scoring_team}! Number was {player_guess}.")

    db[chat_id].pop("pending_kick")
    update_db(chat_id, db[chat_id])
    await msg.answer(f"📊 Current Score:\n🔵 Team A: {db[chat_id]['score']['A']}\n🔴 Team B: {db[chat_id]['score']['B']}")
