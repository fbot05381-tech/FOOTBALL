from aiogram import Router, types
from aiogram.filters import Command
from utils.db import read_json, write_json, MATCH_DB, PLAYER_DB
import asyncio
import random
import time

router = Router()

# ✅ Cooldown Trackers
last_score_time = 0
last_command_time = {}

# ✅ Command Cooldown (10s per user)
def check_cooldown(user_id):
    global last_command_time
    now = time.time()
    if user_id in last_command_time and now - last_command_time[user_id] < 10:
        return False
    last_command_time[user_id] = now
    return True

# ✅ Start Match (Referee Only)
@router.message(Command("start_match"))
async def start_match(message: types.Message):
    if not check_cooldown(message.from_user.id):
        return await message.answer("⏳ Please wait before using commands again.")
    await message.answer("🏆 Match Started!\n\nTeams are being prepared...")
    match_data = {"status": "running", "start_time": time.time(), "score": {"A": 0, "B": 0}, "events": []}
    await write_json(MATCH_DB, match_data)

# ✅ Pause Game
@router.message(Command("pause_game"))
async def pause_game(message: types.Message):
    if not check_cooldown(message.from_user.id):
        return await message.answer("⏳ Please wait before using commands again.")
    match_data = await read_json(MATCH_DB)
    match_data["status"] = "paused"
    await write_json(MATCH_DB, match_data)
    msg = await message.answer("⏸️ <b>Game Paused by Referee</b>")
    await message.pin()

# ✅ Resume Game
@router.message(Command("resume_game"))
async def resume_game(message: types.Message):
    if not check_cooldown(message.from_user.id):
        return await message.answer("⏳ Please wait before using commands again.")
    match_data = await read_json(MATCH_DB)
    match_data["status"] = "running"
    await write_json(MATCH_DB, match_data)
    msg = await message.answer("▶️ <b>Game Resumed!</b>")
    await message.pin()

# ✅ Reset Match
@router.message(Command("reset_match"))
async def reset_match(message: types.Message):
    if not check_cooldown(message.from_user.id):
        return await message.answer("⏳ Please wait before using commands again.")
    await write_json(MATCH_DB, {})
    await message.answer("❌ Match Reset!")

# ✅ Scoreboard (30s Global Cooldown)
@router.message(Command("score"))
async def score(message: types.Message):
    global last_score_time
    if time.time() - last_score_time < 30:
        await message.answer("⏳ Please wait 30s before using /score again.")
        return
    if not check_cooldown(message.from_user.id):
        return await message.answer("⏳ Please wait before using commands again.")
    last_score_time = time.time()

    match_data = await read_json(MATCH_DB)
    score_a = match_data.get("score", {}).get("A", 0)
    score_b = match_data.get("score", {}).get("B", 0)
    await message.answer(f"📊 <b>Scoreboard</b>\n\nTeam A: {score_a}\nTeam B: {score_b}")

# ✅ Time (GIF/Sticker + Text)
@router.message(Command("time"))
async def time_left(message: types.Message):
    if not check_cooldown(message.from_user.id):
        return await message.answer("⏳ Please wait before using commands again.")
    gifs = ["⏱️ Time Running!", "⌛ Hurry up!", "🕒 Clock ticking!"]
    await message.answer(random.choice(gifs))

# ✅ Add Player
@router.message(Command("add_player"))
async def add_player(message: types.Message):
    if not check_cooldown(message.from_user.id):
        return await message.answer("⏳ Please wait before using commands again.")
    if not message.reply_to_message:
        await message.answer("Reply to user or use /add_player @username")
        return
    player_id = message.reply_to_message.from_user.id
    players = await read_json(PLAYER_DB)
    players[str(player_id)] = {"team": "A", "goals": 0, "assists": 0}
    await write_json(PLAYER_DB, players)
    await message.answer(f"✅ Added {message.reply_to_message.from_user.full_name} to Team A")

# ✅ Remove Player A
@router.message(Command("remove_player_a"))
async def remove_player_a(message: types.Message):
    if not check_cooldown(message.from_user.id):
        return await message.answer("⏳ Please wait before using commands again.")
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Usage: /remove_player_a <number>")
        return
    number = args[1]
    await message.answer(f"❌ Removed player #{number} from Team A")

# ✅ Remove Player B
@router.message(Command("remove_player_b"))
async def remove_player_b(message: types.Message):
    if not check_cooldown(message.from_user.id):
        return await message.answer("⏳ Please wait before using commands again.")
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Usage: /remove_player_b <number>")
        return
    number = args[1]
    await message.answer(f"❌ Removed player #{number} from Team B")

# ✅ Pass Logic (Nearby vs Far) + 30s Timeout
@router.message(Command("pass"))
async def pass_ball(message: types.Message):
    if not check_cooldown(message.from_user.id):
        return await message.answer("⏳ Please wait before using commands again.")
    players = await read_json(PLAYER_DB)
    nearby = [p for p in players.keys() if random.choice([True, False])]
    far = [p for p in players.keys() if p not in nearby]
    keyboard = types.InlineKeyboardMarkup()
    for pid in nearby:
        keyboard.add(types.InlineKeyboardButton(text=f"Nearby Player {pid}", callback_data=f"lob:{pid}"))
    for pid in far:
        keyboard.add(types.InlineKeyboardButton(text=f"Far Player {pid}", callback_data=f"long:{pid}"))
    await message.answer("⚽ Choose pass type:\n\nNearby (Lob Pass) or Far (Long Pass)", reply_markup=keyboard)

# ✅ Goal Logic (Auto Goals + Assists)
@router.message(Command("goal"))
async def goal(message: types.Message):
    if not check_cooldown(message.from_user.id):
        return await message.answer("⏳ Please wait before using commands again.")
    match_data = await read_json(MATCH_DB)
    players = await read_json(PLAYER_DB)
    pid = str(message.from_user.id)
    if pid not in players:
        return await message.answer("❌ You are not in the match.")
    players[pid]["goals"] += 1
    if "last_pass" in match_data:
        assist_id = match_data["last_pass"]
        if assist_id in players:
            players[assist_id]["assists"] += 1
    await write_json(PLAYER_DB, players)
    match_data["score"]["A"] += 1
    match_data["events"].append({"type": "goal", "player": pid, "time": time.time()})
    await write_json(MATCH_DB, match_data)
    await message.answer(f"🥅 GOAL by {message.from_user.full_name}!")
