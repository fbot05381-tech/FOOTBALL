import json
import os
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from utils.db import load_json, save_json

router = Router()
DATA_DIR = "database"
TEAMS_FILE = os.path.join(DATA_DIR, "teams.json")

@router.callback_query(F.data == "team_mode")
async def select_team_mode(cb: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="I'm the Referee 🎩", callback_data="be_referee")]
    ])
    await cb.message.answer("Team Mode Selected!\nClick below to become the Referee:", reply_markup=kb)

@router.callback_query(F.data == "be_referee")
async def become_referee(cb: CallbackQuery):
    teams = {"referee": cb.from_user.id, "team_a": [], "team_b": [], "captains": {}, "goalkeepers": {}}
    save_json(TEAMS_FILE, teams)
    await cb.message.answer("You are now the Referee!\nUse /create_team to create teams.")

@router.message(commands=["create_team"])
async def create_team(msg: Message):
    teams = load_json(TEAMS_FILE)
    if msg.from_user.id != teams.get("referee"):
        return await msg.answer("Only Referee can create teams.")
    teams["team_a"] = []
    teams["team_b"] = []
    save_json(TEAMS_FILE, teams)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Join FOOTBALL TEAM A", callback_data="join_A")],
        [InlineKeyboardButton(text="Join FOOTBALL TEAM B", callback_data="join_B")]
    ])
    await msg.answer("Teams created!\nPlayers click below to join:", reply_markup=kb)

@router.callback_query(F.data.startswith("join_"))
async def join_team(cb: CallbackQuery):
    team = cb.data.split("_")[1]
    teams = load_json(TEAMS_FILE)
    user = {"id": cb.from_user.id, "name": cb.from_user.first_name}

    if any(u["id"] == cb.from_user.id for u in teams["team_a"] + teams["team_b"]):
        return await cb.answer("You already joined a team!", show_alert=True)

    if team == "A" and len(teams["team_a"]) < 8:
        teams["team_a"].append(user)
    elif team == "B" and len(teams["team_b"]) < 8:
        teams["team_b"].append(user)
    else:
        return await cb.answer("Team full!", show_alert=True)

    save_json(TEAMS_FILE, teams)
    await cb.message.answer(f"{user['name']} joined FOOTBALL TEAM {team}!")

@router.message(commands=["set_captain"])
async def set_captain(msg: Message):
    args = msg.text.split()
    if len(args) < 2:
        return await msg.answer("Usage: /set_captain @username")
    teams = load_json(TEAMS_FILE)
    if msg.from_user.id != teams.get("referee"):
        return await msg.answer("Only Referee can set captain.")
    teams["captains"][args[1]] = True
    save_json(TEAMS_FILE, teams)
    await msg.answer(f"Captain set: {args[1]}")

@router.message(commands=["gk"])
async def set_goalkeeper(msg: Message):
    args = msg.text.split()
    if len(args) != 3:
        return await msg.answer("Usage: /gk <A/B> <player_index>")
    team, index = args[1], int(args[2]) - 1
    teams = load_json(TEAMS_FILE)
    key = "team_a" if team == "A" else "team_b"
    try:
        player = teams[key][index]
        teams["goalkeepers"][team] = player
        save_json(TEAMS_FILE, teams)
        await msg.answer(f"Goalkeeper for Team {team}: {player['name']}")
    except:
        await msg.answer("Invalid player index.")
