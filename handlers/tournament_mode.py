import os, asyncio
from aiogram import Router, types, F
from aiogram.filters import Command
from utils.db import load_json, save_json

router = Router()
DATA_DIR = "database"
TOURNAMENT_FILE = os.path.join(DATA_DIR, "tournament.json")

@router.callback_query(F.data == "tournament_mode")
async def tournament_mode(cb: types.CallbackQuery):
    data = {
        "owner": None,
        "total_teams": 0,
        "players_per_team": 0,
        "registered_teams": {},
        "tournament_started": False
    }
    save_json(TOURNAMENT_FILE, data)
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="👑 I'm the Owner", callback_data="be_owner")]
    ])
    await cb.message.answer("🏆 Tournament Mode selected!\nChoose an Owner to organize tournament:", reply_markup=kb)

# ✅ Set Owner
@router.callback_query(F.data == "be_owner")
async def be_owner(cb: types.CallbackQuery):
    data = load_json(TOURNAMENT_FILE)
    if data.get("owner"):
        return await cb.answer("Owner already selected!", show_alert=True)
    data["owner"] = cb.from_user.id
    save_json(TOURNAMENT_FILE, data)
    await cb.message.edit_text(f"👑 {cb.from_user.full_name} is now Tournament Owner!\nUse /create_tournament")

# ✅ Create Tournament
@router.message(Command("create_tournament"))
async def create_tournament(msg: types.Message):
    data = load_json(TOURNAMENT_FILE)
    if msg.from_user.id != data.get("owner"):
        return await msg.answer("Only the Owner can create tournament.")

    await msg.answer("✅ Tournament created!\nNow set total teams using /total_team 4-10")

# ✅ Total Teams
@router.message(Command("total_team"))
async def total_team(msg: types.Message):
    data = load_json(TOURNAMENT_FILE)
    if msg.from_user.id != data.get("owner"):
        return await msg.answer("Only Owner can set total teams.")

    parts = msg.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        return await msg.answer("Usage: /total_team 4")
    count = int(parts[1])
    if count < 4 or count > 10:
        return await msg.answer("Teams must be between 4-10.")

    data["total_teams"] = count
    save_json(TOURNAMENT_FILE, data)
    await msg.answer(f"📌 Tournament set for {count} teams.\nNow set players per team using /team_members 4-10")

# ✅ Team Members
@router.message(Command("team_members"))
async def team_members(msg: types.Message):
    data = load_json(TOURNAMENT_FILE)
    if msg.from_user.id != data.get("owner"):
        return await msg.answer("Only Owner can set team members.")

    parts = msg.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        return await msg.answer("Usage: /team_members 5")
    count = int(parts[1])
    if count < 4 or count > 10:
        return await msg.answer("Players per team must be 4-10.")

    data["players_per_team"] = count
    save_json(TOURNAMENT_FILE, data)
    await msg.answer(f"👥 Players per team set to {count}\nNow teams can register!")

# ✅ Register Team (Basic skeleton)
@router.message(Command("register_team"))
async def register_team(msg: types.Message):
    data = load_json(TOURNAMENT_FILE)
    if data["tournament_started"]:
        return await msg.answer("Tournament already started!")

    parts = msg.text.split(maxsplit=2)
    if len(parts) < 3:
        return await msg.answer("Usage: /register_team TeamName @Captain")

    team_name = parts[1]
    if team_name in data["registered_teams"]:
        return await msg.answer("Team name already registered!")

    if not msg.entities or len(msg.entities) < 2 or not msg.entities[1].user:
        return await msg.answer("You must tag the captain.")

    captain_id = msg.entities[1].user.id
    captain_name = msg.entities[1].user.full_name

    data["registered_teams"][team_name] = {
        "captain": {"id": captain_id, "name": captain_name},
        "players": []
    }
    save_json(TOURNAMENT_FILE, data)
    await msg.answer(f"✅ Team '{team_name}' registered with Captain {captain_name}")

# ✅ Start Tournament (skeleton)
@router.message(Command("start_tournament"))
async def start_tournament(msg: types.Message):
    data = load_json(TOURNAMENT_FILE)
    if msg.from_user.id != data.get("owner"):
        return await msg.answer("Only Owner can start tournament.")
    data["tournament_started"] = True
    save_json(TOURNAMENT_FILE, data)
    await msg.answer("🏆 Tournament Started! Matches will be scheduled soon.")
