import asyncio
import random
import time
from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.db import read_json, write_json, MATCH_DB, PLAYER_DB
from utils.rate_limit import check_cooldown

COOLDOWN_GIF = "CgACAgQAAxkBAANHZCoolDownGIFID"  # अपनी GIF का file_id डालना

# Nearby vs Far logic के लिए helper
def get_nearby_and_far(players, current_player):
    idx = players.index(current_player)
    nearby = []
    far = []
    for i, p in enumerate(players):
        if p != current_player:
            if abs(i - idx) <= 1:
                nearby.append(p)
            else:
                far.append(p)
    return nearby, far

# Scoreboard HTML
def generate_scoreboard(match):
    team_a_score = match.get("team_a_score", 0)
    team_b_score = match.get("team_b_score", 0)
    return f"""
<b>📊 SCOREBOARD</b>

<b>Team A:</b> {team_a_score}
<b>Team B:</b> {team_b_score}
"""

# Start Match
async def start_match(message: types.Message, bot):
    if not await check_cooldown(message.from_user.id, "start", bot, message.chat.id):
        return

    match = {"team_a": [], "team_b": [], "team_a_score": 0, "team_b_score": 0, "status": "running"}
    write_json(MATCH_DB, match)

    await message.answer("✅ Match Started!\nUse /add_player to add players.")

# Add Player
async def add_player(message: types.Message, bot):
    if not await check_cooldown(message.from_user.id, "add", bot, message.chat.id):
        return

    match = read_json(MATCH_DB)
    if not match: return await message.answer("⚠️ Start a match first!")

    if message.entities and message.entities[0].type == "mention":
        username = message.text.split()[1]
    elif message.reply_to_message:
        username = f"@{message.reply_to_message.from_user.username}"
    else:
        username = f"@{message.from_user.username}"

    # Alternate Team Assignment
    if len(match["team_a"]) <= len(match["team_b"]):
        match["team_a"].append(username)
    else:
        match["team_b"].append(username)

    write_json(MATCH_DB, match)
    await message.answer(f"👤 {username} added to the match!")

# Remove Player A
async def remove_player_a(message: types.Message):
    match = read_json(MATCH_DB)
    if not match: return await message.answer("⚠️ No active match.")

    try:
        num = int(message.text.split()[1]) - 1
        removed = match["team_a"].pop(num)
        write_json(MATCH_DB, match)
        await message.answer(f"❌ Removed {removed} from Team A")
    except:
        await message.answer("⚠️ Invalid player number.")

# Remove Player B
async def remove_player_b(message: types.Message):
    match = read_json(MATCH_DB)
    if not match: return await message.answer("⚠️ No active match.")

    try:
        num = int(message.text.split()[1]) - 1
        removed = match["team_b"].pop(num)
        write_json(MATCH_DB, match)
        await message.answer(f"❌ Removed {removed} from Team B")
    except:
        await message.answer("⚠️ Invalid player number.")

# Pause Match
async def pause_game(message: types.Message, bot):
    match = read_json(MATCH_DB)
    if not match: return await message.answer("⚠️ No active match.")
    match["status"] = "paused"
    write_json(MATCH_DB, match)
    sent = await message.answer("⏸️ Game Paused by Referee")
    await bot.pin_chat_message(message.chat.id, sent.message_id)

# Resume Match
async def resume_game(message: types.Message, bot):
    match = read_json(MATCH_DB)
    if not match: return await message.answer("⚠️ No active match.")
    match["status"] = "running"
    write_json(MATCH_DB, match)
    sent = await message.answer("▶️ Game Resumed")
    await bot.pin_chat_message(message.chat.id, sent.message_id)

# Scoreboard Command
async def show_score(message: types.Message, bot):
    if not await check_cooldown(message.from_user.id, "score", bot, message.chat.id):
        return

    match = read_json(MATCH_DB)
    if not match: return await message.answer("⚠️ No active match.")

    scoreboard = generate_scoreboard(match)
    await bot.send_animation(message.chat.id, animation=COOLDOWN_GIF, caption=scoreboard, parse_mode="HTML")
