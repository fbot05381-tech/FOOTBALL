import os
from aiogram import Router, types, F
from aiogram.filters import Command, CommandObject
from aiogram.types import CallbackQuery
from utils.db import load_json, save_json

router = Router()
DATA_DIR = "database"
TEAMS_FILE = os.path.join(DATA_DIR, "teams.json")

# ✅ Team Mode selection
@router.callback_query(F.data == "team_mode")
async def team_mode(cb: CallbackQuery):
    teams = {"team_a": [], "team_b": [], "referee": None}
    save_json(TEAMS_FILE, teams)
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="🎩 I'm the Referee", callback_data="be_referee")]
    ])
    await cb.message.answer("Team Mode selected!\n🎩 Choose a Referee:", reply_markup=kb)

# ✅ Become Referee
@router.callback_query(F.data == "be_referee")
async def be_referee(cb: CallbackQuery):
    teams = load_json(TEAMS_FILE)
    teams["referee"] = cb.from_user.id
    save_json(TEAMS_FILE, teams)
    await cb.message.answer(f"🎩 {cb.from_user.full_name} is now the Referee!\nUse /create_team to create teams.")

# ✅ Create Teams
@router.message(Command("create_team"))
async def create_team(msg: types.Message):
    teams = load_json(TEAMS_FILE)
    if msg.from_user.id != teams.get("referee"):
        return await msg.answer("Only Referee can create teams.")
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Join FOOTBALL TEAM A", callback_data="join_A")],
        [types.InlineKeyboardButton(text="Join FOOTBALL TEAM B", callback_data="join_B")]
    ])
    await msg.answer("🏟️ Teams are open!\nPlayers, join your team:", reply_markup=kb)

# ✅ Join Team
@router.callback_query(F.data.startswith("join_"))
async def join_team(cb: CallbackQuery):
    teams = load_json(TEAMS_FILE)
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

# ✅ Choose Captain (Referee command)
@router.message(Command("choose_captain"))
async def choose_captain(msg: types.Message, command: CommandObject):
    args = command.args.split()
    if len(args) != 2:
        return await msg.answer("Usage: /choose_captain <A/B> <user_id>")
    team, user_id = args[0].upper(), int(args[1])
    teams = load_json(TEAMS_FILE)

    if msg.from_user.id != teams.get("referee"):
        return await msg.answer("Only Referee can choose captains.")

    if team not in ["A", "B"]:
        return await msg.answer("Team must be A or B.")

    if team == "A" and not any(p["id"] == user_id for p in teams["team_a"]):
        return await msg.answer("Player not found in Team A.")
    if team == "B" and not any(p["id"] == user_id for p in teams["team_b"]):
        return await msg.answer("Player not found in Team B.")

    teams[f"captain_{team}"] = user_id
    save_json(TEAMS_FILE, teams)
    await msg.answer(f"👑 Captain set for Team {team}: {user_id}")

# ✅ Captain assigns Goalkeeper
@router.message(Command("gk"))
async def set_goalkeeper(msg: types.Message, command: CommandObject):
    args = command.args.split()
    if len(args) != 2:
        return await msg.answer("Usage: /gk <A/B> <user_id>")
    team, user_id = args[0].upper(), int(args[1])
    teams = load_json(TEAMS_FILE)

    captain_id = teams.get(f"captain_{team}")
    if msg.from_user.id != captain_id:
        return await msg.answer("Only the Team Captain can set the Goalkeeper.")

    teams[f"gk_{team}"] = user_id
    save_json(TEAMS_FILE, teams)
    await msg.answer(f"🧤 Goalkeeper set for Team {team}: {user_id}")

# ✅ Referee can change Goalkeeper anytime
@router.message(Command("change_GK"))
async def change_goalkeeper(msg: types.Message, command: CommandObject):
    args = command.args.split()
    if len(args) != 2:
        return await msg.answer("Usage: /change_GK <A/B> <new_user_id>")
    team, user_id = args[0].upper(), int(args[1])
    teams = load_json(TEAMS_FILE)

    if msg.from_user.id != teams.get("referee"):
        return await msg.answer("Only Referee can change Goalkeeper.")

    teams[f"gk_{team}"] = user_id
    save_json(TEAMS_FILE, teams)
    await msg.answer(f"🔄 Goalkeeper for Team {team} changed to: {user_id}")
