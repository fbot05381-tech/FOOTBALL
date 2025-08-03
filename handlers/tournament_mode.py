from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, ChatMemberUpdated
import os, json

router = Router()
TOURNAMENT_FILE = "database/tournament_data.json"

# ✅ Load/Save Tournament Data
def load_tournament():
    if not os.path.exists(TOURNAMENT_FILE):
        return {"owner": None, "teams": {}, "matches": [], "points": {}, "active": False}
    with open(TOURNAMENT_FILE, "r") as f:
        return json.load(f)

def save_tournament(data):
    with open(TOURNAMENT_FILE, "w") as f:
        json.dump(data, f, indent=4)

async def is_admin(msg: Message):
    member = await msg.chat.get_member(msg.from_user.id)
    return member.is_chat_admin()

# ✅ Create Tournament
@router.message(Command("create_tournament"))
async def create_tournament(msg: Message):
    data = load_tournament()
    if data["active"]:
        return await msg.answer("❌ A tournament is already running! Use /end_tournament to reset.")
    data["owner"] = msg.from_user.id
    data["active"] = True
    save_tournament(data)
    await msg.answer("🏆 Tournament created!\n✅ Use /total_team to set number of teams.")

# ✅ Set Total Teams
@router.message(Command("total_team"))
async def total_team(msg: Message):
    data = load_tournament()
    if msg.from_user.id != data["owner"] and not await is_admin(msg):
        return await msg.answer("❌ Only the tournament owner or group admin can set total teams.")
    parts = msg.text.split()
    if len(parts) < 2 or not parts[1].isdigit():
        return await msg.answer("⚠ Usage: /total_team <number>")
    total = int(parts[1])
    data["total_teams"] = total
    save_tournament(data)
    await msg.answer(f"✅ Tournament will have **{total} teams**.\nUse /register_team <TeamName> @Captain to register.")

# ✅ Register Teams
@router.message(Command("register_team"))
async def register_team(msg: Message):
    data = load_tournament()
    if not data.get("total_teams"):
        return await msg.answer("⚠ Use /total_team first to set total teams.")
    parts = msg.text.split()
    if len(parts) < 3:
        return await msg.answer("⚠ Usage: /register_team <TeamName> @Captain")
    team_name = parts[1]
    captain = parts[2]
    if team_name in data["teams"]:
        return await msg.answer("❌ Team name already registered.")
    data["teams"][team_name] = captain
    data["points"][team_name] = 0
    save_tournament(data)
    await msg.answer(f"✅ Registered **{team_name}** with Captain {captain}")

# ✅ Points Table
@router.message(Command("points"))
async def points(msg: Message):
    data = load_tournament()
    if not data["active"]:
        return await msg.answer("⚠ No active tournament.")
    table = "📊 **POINTS TABLE**\n\n"
    for team, pts in data["points"].items():
        table += f"🏆 {team}: {pts} pts\n"
    await msg.answer(table)

# ✅ End Tournament (Owner or Admin)
@router.message(Command("end_tournament"))
async def end_tournament(msg: Message):
    data = load_tournament()
    if msg.from_user.id != data["owner"] and not await is_admin(msg):
        return await msg.answer("❌ Only the tournament owner or group admin can end the tournament!")

    save_tournament({"owner": None, "teams": {}, "matches": [], "points": {}, "active": False})
    await msg.answer("🛑 Tournament ended!\n✅ All data cleared. Ready for a new tournament.")
