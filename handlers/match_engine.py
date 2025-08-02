import os, random, asyncio, time
from aiogram import Router, types
from aiogram.filters import Command
from utils.db import load_json, save_json

router = Router()
DATA_DIR = "database"
TEAMS_FILE = os.path.join(DATA_DIR, "teams.json")

ROUND_TIME = 15 * 60  # 15 min (can adjust)
MOVE_TIMEOUT = 15

@router.message(Command("start_match"))
async def start_match(msg: types.Message):
    teams = load_json(TEAMS_FILE)
    if msg.from_user.id != teams.get("referee"):
        return await msg.answer("Only Referee can start the match.")
    if teams.get("game_started"):
        return await msg.answer("Game already started!")

    teams["game_started"] = True
    save_json(TEAMS_FILE, teams)

    await msg.answer("🏁 Match Starting in 3...2...1...")
    await asyncio.sleep(3)
    await msg.answer("🪙 Tossing coin for ball possession...")

    cap_a = teams.get("captain_a")
    cap_b = teams.get("captain_b")

    if not cap_a or not cap_b:
        return await msg.answer("Both teams must have captains using /captain @username")

    toss_winner = random.choice([cap_a, cap_b])
    teams["ball"] = toss_winner
    save_json(TEAMS_FILE, teams)

    await msg.answer(f"🎉 Ball goes to <b>{toss_winner}</b>! Use KICK/DEFENSIVE/PASS to play.")

@router.message(Command("end_match"))
async def end_match(msg: types.Message):
    teams = load_json(TEAMS_FILE)
    if msg.from_user.id != teams.get("referee"):
        return await msg.answer("Only Referee can end the match.")

    teams["game_started"] = False
    save_json(TEAMS_FILE, teams)
    await msg.answer("⏹️ Match Ended.")

# ✅ Captain selection
@router.message(Command("captain"))
async def choose_captain(msg: types.Message):
    teams = load_json(TEAMS_FILE)
    if msg.from_user.id != teams.get("referee"):
        return await msg.answer("Only Referee can choose captain.")

    if not msg.entities or len(msg.entities) < 2 or not msg.entities[1].user:
        return await msg.answer("Usage: /captain @username A/B")

    target = msg.entities[1].user.full_name
    dest_team = msg.text.split()[-1].upper()
    if dest_team == "A":
        teams["captain_a"] = target
    else:
        teams["captain_b"] = target

    save_json(TEAMS_FILE, teams)
    await msg.answer(f"👑 {target} is now Captain of Team {dest_team}")

# ✅ Goalkeeper set/change
@router.message(Command("gk"))
async def set_goalkeeper(msg: types.Message):
    teams = load_json(TEAMS_FILE)
    if msg.from_user.id != teams.get("referee"):
        return await msg.answer("Only Referee can set Goalkeeper.")

    parts = msg.text.split()
    if len(parts) != 3:
        return await msg.answer("Usage: /gk A 1")

    team, num = parts[1], parts[2]
    teams[f"gk_{team.lower()}"] = num
    save_json(TEAMS_FILE, teams)
    await msg.answer(f"🧤 Goalkeeper of Team {team.upper()} set to Player {num}")

@router.message(Command("change_gk"))
async def change_goalkeeper(msg: types.Message):
    teams = load_json(TEAMS_FILE)
    if msg.from_user.id != teams.get("referee"):
        return await msg.answer("Only Referee can change Goalkeeper.")

    parts = msg.text.split()
    if len(parts) != 4:
        return await msg.answer("Usage: /change_gk A 5")

    team, old_num, new_num = parts[1], parts[2], parts[3]
    teams[f"gk_{team.lower()}"] = new_num
    save_json(TEAMS_FILE, teams)
    await msg.answer(f"🔄 Goalkeeper changed in Team {team.upper()} from Player {old_num} to Player {new_num}")
