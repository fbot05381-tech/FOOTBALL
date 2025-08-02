import os
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery
from utils.db import load_json, save_json

router = Router()
DATA_DIR = "database"
TEAMS_FILE = os.path.join(DATA_DIR, "teams.json")

@router.callback_query(F.data == "team_mode")
async def team_mode(cb: CallbackQuery):
    teams = {"team_a": [], "team_b": [], "referee": None}
    save_json(TEAMS_FILE, teams)
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="🎩 I'm the Referee", callback_data="be_referee")]
    ])
    await cb.message.answer("Team Mode selected!\n🎩 Choose a Referee:", reply_markup=kb)

@router.callback_query(F.data == "be_referee")
async def be_referee(cb: CallbackQuery):
    teams = load_json(TEAMS_FILE)
    teams["referee"] = cb.from_user.id
    save_json(TEAMS_FILE, teams)
    await cb.message.answer(f"🎩 {cb.from_user.full_name} is now the Referee!\nUse /create_team to create teams.")

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
