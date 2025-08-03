from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.db import read_json, write_json, MATCH_DB, PLAYER_DB
import asyncio, time

router = Router()

COOLDOWN_SCORE = {}
COOLDOWN_COMMAND = {}

async def check_cooldown(user_id, cmd, cooldown):
    now = time.time()
    if cmd in COOLDOWN_COMMAND and now - COOLDOWN_COMMAND[cmd] < cooldown:
        return False
    COOLDOWN_COMMAND[cmd] = now
    return True

@router.message(Command("start_match"))
async def start_match(message: Message):
    data = read_json(MATCH_DB)
    data["status"] = "running"
    write_json(MATCH_DB, data)
    await message.answer("✅ Match started!")

@router.message(Command("pause_game"))
async def pause_game(message: Message):
    data = read_json(MATCH_DB)
    data["status"] = "paused"
    write_json(MATCH_DB, data)
    await message.answer("⏸ Game paused!")

@router.message(Command("resume_game"))
async def resume_game(message: Message):
    data = read_json(MATCH_DB)
    data["status"] = "running"
    write_json(MATCH_DB, data)
    await message.answer("▶️ Game resumed!")

@router.message(Command("score"))
async def score(message: Message):
    user_id = message.from_user.id
    now = time.time()
    if user_id in COOLDOWN_SCORE and now - COOLDOWN_SCORE[user_id] < 30:
        await message.answer("⏳ Please wait before using /score again!")
        return
    COOLDOWN_SCORE[user_id] = now
    await message.answer("📊 Scoreboard updated with GIF/Sticker!")

@router.message(Command("add_player"))
async def add_player(message: Message):
    args = message.text.split()
    if len(args) < 2:
        await message.answer("⚠️ Usage: /add_player @username")
        return
    await message.answer(f"✅ Player {args[1]} added!")

@router.message(Command("remove_player_A"))
async def remove_player_a(message: Message):
    args = message.text.split()
    if len(args) < 2:
        await message.answer("⚠️ Usage: /remove_player_A <number>")
        return
    await message.answer(f"❌ Player #{args[1]} removed from Team A")

@router.message(Command("remove_player_B"))
async def remove_player_b(message: Message):
    args = message.text.split()
    if len(args) < 2:
        await message.answer("⚠️ Usage: /remove_player_B <number>")
        return
    await message.answer(f"❌ Player #{args[1]} removed from Team B")

@router.message(Command("set_referee"))
async def set_referee(message: Message):
    args = message.text.split()
    if len(args) < 2:
        await message.answer("⚠️ Usage: /set_referee @username")
        return
    data = read_json(MATCH_DB)
    data["referee"] = args[1]
    write_json(MATCH_DB, data)
    await message.answer(f"👨‍⚖️ Referee set to {args[1]}")
