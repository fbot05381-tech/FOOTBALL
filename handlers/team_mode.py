from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
import time, asyncio
from utils.db import load_json, save_json

router = Router()
DB_FILE = "database/team_mode.json"

join_window = {}

# ✅ Start Team Mode
@router.callback_query(F.data == "team_mode")
async def team_mode_entry(cb: CallbackQuery):
    data = load_json(DB_FILE)
    chat_id = str(cb.message.chat.id)

    data[chat_id] = {
        "referee": None,
        "teamA": [],
        "teamB": [],
        "captains": {},
        "goalkeepers": {},
        "match_started": False,
        "join_start": None
    }
    save_json(DB_FILE, data)

    await cb.message.answer("🏟️ Team Mode Started!\nUse /create_team to allow players to join.")

# ✅ Referee select
@router.callback_query(F.data == "be_referee")
async def set_referee(cb: CallbackQuery):
    data = load_json(DB_FILE)
    chat_id = str(cb.message.chat.id)
    user = cb.from_user.username or cb.from_user.first_name

    if data.get(chat_id, {}).get("referee"):
        await cb.answer("Referee already selected!", show_alert=True)
        return

    data[chat_id]["referee"] = user
    save_json(DB_FILE, data)

    await cb.message.answer(f"👨‍⚖️ Referee: @{user}\n\nUse /create_team to start team joining.")

# ✅ Create Teams (Referee Only)
@router.message(Command("create_team"))
async def create_team(msg: Message):
    data = load_json(DB_FILE)
    chat_id = str(msg.chat.id)
    user = msg.from_user.username or msg.from_user.first_name

    if chat_id not in data or data[chat_id]["referee"] != user:
        await msg.answer("❌ Only referee can use this command!")
        return

    data[chat_id]["teamA"] = []
    data[chat_id]["teamB"] = []
    data[chat_id]["join_start"] = time.time()
    save_json(DB_FILE, data)

    await msg.answer("⏳ 2 minutes to join teams!\nPlayers, use /join_football to join Team A or Team B.")

    # Alerts at 30s & 15s
    await asyncio.sleep(90)
    await msg.answer("⚠️ 30 seconds left! Use /join_football to join.")
    await asyncio.sleep(15)
    await msg.answer("⚠️ 15 seconds left! Last chance to use /join_football.")

    await asyncio.sleep(15)
    await finalize_teams(msg.chat.id, msg)

# ✅ Join Football Command
@router.message(Command("join_football"))
async def join_football(msg: Message):
    data = load_json(DB_FILE)
    chat_id = str(msg.chat.id)
    user = msg.from_user.username or msg.from_user.first_name

    if chat_id not in data or not data[chat_id]["join_start"]:
        await msg.answer("❌ No active join window!")
        return

    if time.time() - data[chat_id]["join_start"] > 120:
        await msg.answer("⏰ Joining closed!")
        return

    if user in data[chat_id]["teamA"] or user in data[chat_id]["teamB"]:
        await msg.answer("Already joined a team!")
        return

    # Alternate join (balance teams automatically)
    if len(data[chat_id]["teamA"]) <= len(data[chat_id]["teamB"]):
        data[chat_id]["teamA"].append(user)
        await msg.answer(f"🔵 @{user} joined Team A")
    else:
        data[chat_id]["teamB"].append(user)
        await msg.answer(f"🔴 @{user} joined Team B")

    save_json(DB_FILE, data)

# ✅ Finalize Teams & Pin
async def finalize_teams(chat_id, msg_obj):
    data = load_json(DB_FILE)
    chat_id = str(chat_id)

    if chat_id not in data:
        return

    teamA = data[chat_id]["teamA"]
    teamB = data[chat_id]["teamB"]

    if len(teamA) != len(teamB) or len(teamA) == 0:
        await msg_obj.answer("⚠️ Teams not balanced or empty! Referee can restart with /create_team.")
        return

    # Auto-assign first players as captains
    if teamA: data[chat_id]["captains"]["A"] = teamA[0]
    if teamB: data[chat_id]["captains"]["B"] = teamB[0]

    # Auto-assign second players as GK if exist
    if len(teamA) > 1: data[chat_id]["goalkeepers"]["A"] = teamA[1]
    if len(teamB) > 1: data[chat_id]["goalkeepers"]["B"] = teamB[1]

    save_json(DB_FILE, data)

    listA = "\n".join([f"🔵 {p}{' (C)' if p == data[chat_id]['captains'].get('A') else ''}{' (GK)' if p == data[chat_id]['goalkeepers'].get('A') else ''}" for p in teamA])
    listB = "\n".join([f"🔴 {p}{' (C)' if p == data[chat_id]['captains'].get('B') else ''}{' (GK)' if p == data[chat_id]['goalkeepers'].get('B') else ''}" for p in teamB])

    msg = await msg_obj.answer(f"🏟️ <b>Teams Finalized</b>\n\n<b>Team A</b>:\n{listA}\n\n<b>Team B</b>:\n{listB}")
    await msg.pin()

# ✅ Change Captain
@router.message(Command("set_captain"))
async def set_captain(msg: Message):
    args = msg.text.split()
    if len(args) < 3:
        await msg.answer("Usage: /set_captain A @username")
        return

    data = load_json(DB_FILE)
    chat_id = str(msg.chat.id)
    team = args[1].upper()
    user = args[2].replace("@", "")

    if team not in ["A", "B"]:
        await msg.answer("Team must be A or B!")
        return

    data[chat_id]["captains"][team] = user
    save_json(DB_FILE, data)
    await msg.answer(f"✅ @{user} is now Captain of Team {team}")

# ✅ Change Goalkeeper
@router.message(Command("set_gk"))
async def set_gk(msg: Message):
    args = msg.text.split()
    if len(args) < 3:
        await msg.answer("Usage: /set_gk A @username")
        return

    data = load_json(DB_FILE)
    chat_id = str(msg.chat.id)
    team = args[1].upper()
    user = args[2].replace("@", "")

    if team not in ["A", "B"]:
        await msg.answer("Team must be A or B!")
        return

    data[chat_id]["goalkeepers"][team] = user
    save_json(DB_FILE, data)
    await msg.answer(f"✅ @{user} is now Goalkeeper of Team {team}")
