import os, asyncio, time
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery
from utils.db import load_json, save_json

router = Router()
DATA_DIR = "database"
TEAMS_FILE = os.path.join(DATA_DIR, "teams.json")

JOIN_LIMIT = 120  # 2 minutes join limit

@router.message(Command("start_football"))
async def start_football(msg: types.Message):
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="⚽ Team Mode", callback_data="team_mode")],
        [types.InlineKeyboardButton(text="🏆 Tournament Mode", callback_data="tournament_mode")]
    ])
    await msg.answer("Choose Football Mode:", reply_markup=kb)

# ✅ Team Mode
@router.callback_query(F.data == "team_mode")
async def team_mode(cb: CallbackQuery):
    teams = {
        "team_a": [],
        "team_b": [],
        "referee": None,
        "game_started": False,
        "join_open": False,
        "join_start_time": 0
    }
    save_json(TEAMS_FILE, teams)
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="🎩 I'm the Referee", callback_data="be_referee")]
    ])
    await cb.message.answer("🎮 Team Mode selected!\nChoose a Referee:", reply_markup=kb)

# ✅ Referee Select
@router.callback_query(F.data == "be_referee")
async def be_referee(cb: CallbackQuery):
    teams = load_json(TEAMS_FILE)
    if teams.get("referee"):
        return await cb.answer("Referee already selected!", show_alert=True)
    teams["referee"] = cb.from_user.id
    save_json(TEAMS_FILE, teams)
    await cb.message.edit_text(f"🎩 {cb.from_user.full_name} is now the Referee!\nUse /create_team to create teams.")

# ✅ Create Teams (2 min join)
@router.message(Command("create_team"))
async def create_team(msg: types.Message):
    teams = load_json(TEAMS_FILE)
    if msg.from_user.id != teams.get("referee"):
        return await msg.answer("Only Referee can create teams.")

    teams["join_open"] = True
    teams["join_start_time"] = int(time.time())
    save_json(TEAMS_FILE, teams)

    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Join FOOTBALL TEAM A", callback_data="join_A")],
        [types.InlineKeyboardButton(text="Join FOOTBALL TEAM B", callback_data="join_B")]
    ])
    await msg.answer("🏟️ Teams are open for 2 minutes!\nPlayers, join your team:", reply_markup=kb)
    asyncio.create_task(close_join_after_time())

async def close_join_after_time():
    await asyncio.sleep(JOIN_LIMIT)
    teams = load_json(TEAMS_FILE)
    teams["join_open"] = False
    save_json(TEAMS_FILE, teams)

# ✅ Join Team
@router.callback_query(F.data.startswith("join_"))
async def join_team(cb: CallbackQuery):
    teams = load_json(TEAMS_FILE)
    if not teams.get("join_open") or (int(time.time()) - teams["join_start_time"] > JOIN_LIMIT):
        return await cb.answer("⏱️ Join window closed! Ask Referee to add you manually.", show_alert=True)

    team = cb.data.split("_")[1]
    player = {"id": cb.from_user.id, "name": cb.from_user.full_name}

    if any(p["id"] == cb.from_user.id for p in teams["team_a"] + teams["team_b"]):
        return await cb.answer("You already joined a team!", show_alert=True)

    if team == "A":
        teams["team_a"].append(player)
    else:
        teams["team_b"].append(player)

    save_json(TEAMS_FILE, teams)
    await cb.message.answer(f"✅ {cb.from_user.full_name} joined FOOTBALL TEAM {team}")

# ✅ Add Member manually
@router.message(Command("add_member"))
async def add_member(msg: types.Message):
    teams = load_json(TEAMS_FILE)
    if msg.from_user.id != teams.get("referee"):
        return await msg.answer("Only Referee can add members.")

    if not msg.entities or len(msg.entities) < 2 or not msg.entities[1].user:
        return await msg.answer("Usage: /add_member @username A/B")

    target_id = msg.entities[1].user.id
    target_name = msg.entities[1].user.full_name
    dest_team = msg.text.split()[-1].upper()

    if dest_team not in ["A", "B"]:
        return await msg.answer("Destination must be A or B.")

    if any(p["id"] == target_id for p in teams["team_a"] + teams["team_b"]):
        return await msg.answer("Player already in a team.")

    teams[f"team_{dest_team.lower()}"].append({"id": target_id, "name": target_name})
    save_json(TEAMS_FILE, teams)
    await msg.answer(f"➕ {target_name} added to FOOTBALL TEAM {dest_team} by Referee.")

# ✅ Shift Member Auto Opposite
@router.message(Command("shift_member"))
async def shift_member(msg: types.Message):
    teams = load_json(TEAMS_FILE)
    if msg.from_user.id != teams.get("referee"):
        return await msg.answer("Only Referee can shift members.")

    if not msg.entities or len(msg.entities) < 2 or not msg.entities[1].user:
        return await msg.answer("Usage: /shift_member @username")

    target_id = msg.entities[1].user.id
    target_name = msg.entities[1].user.full_name

    if any(p["id"] == target_id for p in teams["team_a"]):
        teams["team_a"] = [p for p in teams["team_a"] if p["id"] != target_id]
        teams["team_b"].append({"id": target_id, "name": target_name})
        dest = "B"
    elif any(p["id"] == target_id for p in teams["team_b"]):
        teams["team_b"] = [p for p in teams["team_b"] if p["id"] != target_id]
        teams["team_a"].append({"id": target_id, "name": target_name})
        dest = "A"
    else:
        return await msg.answer("Player is not in any team.")

    save_json(TEAMS_FILE, teams)
    await msg.answer(f"🔄 {target_name} shifted to FOOTBALL TEAM {dest}")
