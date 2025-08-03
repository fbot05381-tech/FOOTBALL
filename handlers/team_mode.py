from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from utils.db import read_db, update_db

router = Router()

# ✅ Create Teams
@router.message(Command("create_team"))
async def create_team(msg: Message):
    db = read_db()
    chat_id = str(msg.chat.id)

    db[chat_id] = {
        "referee": msg.from_user.id,
        "teamA": [],
        "teamB": [],
        "captains": {},
        "goalkeepers": {}
    }

    update_db(chat_id, db[chat_id])
    await msg.answer("✅ Teams created!\nPlayers can join using /join_football.")

# ✅ Join Football
@router.message(Command("join_football"))
async def join_football(msg: Message):
    db = read_db()
    chat_id = str(msg.chat.id)

    if chat_id not in db or "teamA" not in db[chat_id]:
        await msg.answer("❌ Teams are not created yet. Referee should use /create_team first.")
        return

    user_id = msg.from_user.id
    username = msg.from_user.username or msg.from_user.full_name

    # Already in team check
    for p in db[chat_id]["teamA"] + db[chat_id]["teamB"]:
        if p["id"] == user_id:
            await msg.answer("⚠️ You are already in a team!")
            return

    player = {"id": user_id, "name": username}

    if len(db[chat_id]["teamA"]) <= len(db[chat_id]["teamB"]):
        db[chat_id]["teamA"].append(player)
        team = "Team A"
    else:
        db[chat_id]["teamB"].append(player)
        team = "Team B"

    update_db(chat_id, db[chat_id])
    await msg.answer(f"✅ @{username} joined {team}!")

# ✅ Show Teams
@router.message(Command("show_teams"))
async def show_teams(msg: Message):
    db = read_db()
    chat_id = str(msg.chat.id)

    if chat_id not in db or "teamA" not in db[chat_id]:
        await msg.answer("❌ Teams not created yet.")
        return

    text = "🏆 <b>Current Teams</b>\n\n"

    text += "🔵 <b>Team A:</b>\n"
    for p in db[chat_id]["teamA"]:
        tag = " (C)" if p["name"] in db[chat_id]["captains"] else ""
        gk = " (GK)" if p["name"] in db[chat_id]["goalkeepers"] else ""
        text += f" - @{p['name']}{tag}{gk}\n"

    text += "\n🔴 <b>Team B:</b>\n"
    for p in db[chat_id]["teamB"]:
        tag = " (C)" if p["name"] in db[chat_id]["captains"] else ""
        gk = " (GK)" if p["name"] in db[chat_id]["goalkeepers"] else ""
        text += f" - @{p['name']}{tag}{gk}\n"

    await msg.answer(text, parse_mode="HTML")

# ✅ Set Captain
@router.message(Command("set_captain"))
async def set_captain(msg: Message):
    db = read_db()
    chat_id = str(msg.chat.id)

    if chat_id not in db:
        await msg.answer("❌ Teams not created yet.")
        return

    args = msg.text.split()
    if len(args) < 2:
        await msg.answer("⚠️ Usage: /set_captain username")
        return

    username = args[1].replace("@", "")
    db[chat_id]["captains"][username] = True
    update_db(chat_id, db[chat_id])
    await msg.answer(f"✅ @{username} is now Captain!")

# ✅ Set Goalkeeper
@router.message(Command("set_gk"))
async def set_gk(msg: Message):
    db = read_db()
    chat_id = str(msg.chat.id)

    if chat_id not in db:
        await msg.answer("❌ Teams not created yet.")
        return

    args = msg.text.split()
    if len(args) < 2:
        await msg.answer("⚠️ Usage: /set_gk username")
        return

    username = args[1].replace("@", "")
    db[chat_id]["goalkeepers"][username] = True
    update_db(chat_id, db[chat_id])
    await msg.answer(f"🧤 @{username} is now Goalkeeper!")
