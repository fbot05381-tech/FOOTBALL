from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from utils.db import read_db, update_db

router = Router()

# ✅ Create Tournament
@router.message(Command("create_tournament"))
async def create_tournament(msg: Message):
    db = read_db()
    chat_id = str(msg.chat.id)

    db[chat_id] = {
        "owner": msg.from_user.id,
        "teams": {},
        "matches": [],
        "points": {}
    }

    update_db(chat_id, db[chat_id])
    await msg.answer("🏆 Tournament Created!\nUse /register_team TeamName to register teams.")

# ✅ Register Team
@router.message(Command("register_team"))
async def register_team(msg: Message):
    db = read_db()
    chat_id = str(msg.chat.id)

    if chat_id not in db or "owner" not in db[chat_id]:
        await msg.answer("❌ Tournament not created yet.")
        return

    args = msg.text.split(maxsplit=1)
    if len(args) < 2:
        await msg.answer("⚠️ Usage: /register_team TeamName")
        return

    team_name = args[1]
    db[chat_id]["teams"][team_name] = []
    db[chat_id]["points"][team_name] = 0
    update_db(chat_id, db[chat_id])
    await msg.answer(f"✅ Team '{team_name}' registered!")

# ✅ Show Tournament Teams
@router.message(Command("show_tournament"))
async def show_tournament(msg: Message):
    db = read_db()
    chat_id = str(msg.chat.id)

    if chat_id not in db or "teams" not in db[chat_id]:
        await msg.answer("❌ No tournament found.")
        return

    text = "🏆 <b>Tournament Teams</b>\n\n"
    for team in db[chat_id]["teams"]:
        text += f" - {team}\n"

    await msg.answer(text, parse_mode="HTML")

# ✅ End Tournament (Owner Only)
@router.message(Command("end_tournament"))
async def end_tournament(msg: Message):
    db = read_db()
    chat_id = str(msg.chat.id)

    if chat_id not in db:
        await msg.answer("❌ No active tournament.")
        return

    if msg.from_user.id != db[chat_id].get("owner"):
        await msg.answer("⛔ Only the tournament owner can end it.")
        return

    db.pop(chat_id)
    update_db(chat_id, {})
    await msg.answer("🏁 Tournament Ended!")
