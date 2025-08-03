import asyncio, random, logging
from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.db import read_json, write_json, MATCH_DB, PLAYER_DB
from utils.reminder import reminder_loop, stop_reminder, pause_reminder, resume_reminder
from utils.rate_limit import can_use_command

match_data = {"active": False, "paused": False, "score": {"A": 0, "B": 0}, "players": {"A": [], "B": []}, "goals": {}, "assists": {}}

def get_scoreboard():
    score_text = f"🏆 Score:\nA: {match_data['score']['A']} | B: {match_data['score']['B']}"
    gif_id = "CgACAgQAAxkBAAEB12345GIFexample"
    return score_text, gif_id

async def start_match(message: types.Message, bot):
    ok, msg = can_use_command(message.from_user.id, "start")
    if not ok:
        return await message.answer(msg)

    if match_data["active"]:
        return await message.answer("⚠️ Match already running!")

    match_data["active"] = True
    match_data["paused"] = False
    match_data["score"] = {"A": 0, "B": 0}
    write_json(MATCH_DB, match_data)

    await message.answer("✅ Match started!")
    asyncio.create_task(reminder_loop(bot, message.chat.id, get_scoreboard))

async def pause_game(message: types.Message):
    ok, msg = can_use_command(message.from_user.id, "pause")
    if not ok:
        return await message.answer(msg)

    if not match_data["active"]:
        return await message.answer("⚠️ No active match.")
    match_data["paused"] = True
    pause_reminder()
    await message.answer("⏸️ Game paused.")

async def resume_game(message: types.Message):
    ok, msg = can_use_command(message.from_user.id, "resume")
    if not ok:
        return await message.answer(msg)

    if not match_data["active"]:
        return await message.answer("⚠️ No active match.")
    match_data["paused"] = False
    resume_reminder()
    await message.answer("▶️ Game resumed.")

async def end_match(message: types.Message):
    ok, msg = can_use_command(message.from_user.id, "end")
    if not ok:
        return await message.answer(msg)

    if not match_data["active"]:
        return await message.answer("⚠️ No match running.")
    stop_reminder()
    match_data["active"] = False
    write_json(MATCH_DB, match_data)
    await message.answer("🏁 Match ended! Stats saved.")

async def score_command(message: types.Message):
    ok, msg = can_use_command(message.from_user.id, "score")
    if not ok:
        return await message.answer(msg)

    scoreboard_text, gif_id = get_scoreboard()
    await message.answer_animation(animation=gif_id, caption=f"📊 Current Score:\n\n{scoreboard_text}")
