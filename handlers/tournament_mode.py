from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
import random, time
from utils.db import load_json, save_json

router = Router()
DB_FILE = "database/tournament.json"

# ✅ Tournament Mode Entry
@router.callback_query(F.data == "tournament_mode")
async def tournament_mode_entry(cb: CallbackQuery):
    data = load_json(DB_FILE)
    chat_id = str(cb.message.chat.id)

    data[chat_id] = {
        "owner": cb.from_user.username or cb.from_user.first_name,
        "total_teams": 0,
        "team_members": [4, 10],
        "teams": {},
        "fixtures": [],
        "points": {},
        "active": False
    }
    save_json(DB_FILE, data)

    await cb.message.answer("🏆 Tournament Mode Started!\nUse /create_tournament to begin.")

# ✅ Create Tournament (Owner Only)
@router.message(Command("create_tournament"))
async def create_tournament(msg: Message):
    data = load_json(DB_FILE)
    chat_id = str(msg.chat.id)
    user = msg.from_user.username or msg.from_user.first_name

    if chat_id not in data or data[chat_id]["owner"] != user:
        await msg.answer("❌ Only owner can create tournament!")
        return

    data[chat_id]["active"] = True
    save_json(DB_FILE, data)
    await msg.answer("✅ Tournament Created!\nNow set total teams using /total_team X")

# ✅ Set Total Teams
@router.message(Command("total_team"))
async def total_team(msg: Message):
    args = msg.text.split()
    if len(args) < 2 or not args[1].isdigit():
        await msg.answer("Usage: /total_team 4-10")
        return

    data = load_json(DB_FILE)
    chat_id = str(msg.chat.id)
    total = int(args[1])
    data[chat_id]["total_teams"] = total
    save_json(DB_FILE, data)

    await msg.answer(f"✅ Tournament will have {total} teams.\nNow set members using /team_members min-max")

# ✅ Set Team Members
@router.message(Command("team_members"))
async def team_members(msg: Message):
    args = msg.text.split()
    if len(args) < 3:
        await msg.answer("Usage: /team_members 4 10")
        return

    data = load_json(DB_FILE)
    chat_id = str(msg.chat.id)
    min_m, max_m = int(args[1]), int(args[2])
    data[chat_id]["team_members"] = [min_m, max_m]
    save_json(DB_FILE, data)

    await msg.answer(f"✅ Teams can have {min_m}-{max_m} players.\nOwner can now add teams with /add_team <TeamName> @Captain")

# ✅ Add Team
@router.message(Command("add_team"))
async def add_team(msg: Message):
    args = msg.text.split()
    if len(args) < 3:
        await msg.answer("Usage: /add_team TeamName @Captain")
        return

    data = load_json(DB_FILE)
    chat_id = str(msg.chat.id)
    team_name = args[1]
    captain = args[2].replace("@", "")

    data[chat_id]["teams"][team_name] = {
        "captain": captain,
        "players": []
    }
    data[chat_id]["points"][team_name] = 0
    save_json(DB_FILE, data)

    await msg.answer(f"✅ Team <b>{team_name}</b> added with Captain @{captain}")

# ✅ Generate Fixtures
@router.message(Command("generate_fixtures"))
async def generate_fixtures(msg: Message):
    data = load_json(DB_FILE)
    chat_id = str(msg.chat.id)
    teams = list(data[chat_id]["teams"].keys())

    if len(teams) < 2:
        await msg.answer("❌ Not enough teams to generate fixtures!")
        return

    fixtures = []
    for i in range(len(teams)):
        for j in range(i+1, len(teams)):
            fixtures.append((teams[i], teams[j]))

    random.shuffle(fixtures)
    data[chat_id]["fixtures"] = fixtures
    save_json(DB_FILE, data)

    text = "📅 <b>Fixtures</b>\n"
    for idx, match in enumerate(fixtures, start=1):
        text += f"{idx}. {match[0]} 🆚 {match[1]}\n"

    await msg.answer(text)

# ✅ Update Points
@router.message(Command("update_points"))
async def update_points(msg: Message):
    args = msg.text.split()
    if len(args) < 3:
        await msg.answer("Usage: /update_points TeamName Points")
        return

    data = load_json(DB_FILE)
    chat_id = str(msg.chat.id)
    team_name = args[1]
    pts = int(args[2])

    if team_name not in data[chat_id]["points"]:
        await msg.answer("❌ Team not found!")
        return

    data[chat_id]["points"][team_name] += pts
    save_json(DB_FILE, data)

    await msg.answer(f"✅ {team_name} now has {data[chat_id]['points'][team_name]} points")

# ✅ Points Table
@router.message(Command("points_table"))
async def points_table(msg: Message):
    data = load_json(DB_FILE)
    chat_id = str(msg.chat.id)

    points = sorted(data[chat_id]["points"].items(), key=lambda x: x[1], reverse=True)
    text = "🏆 <b>Points Table</b>\n"
    for t, p in points:
        text += f"{t}: {p} pts\n"

    await msg.answer(text)

# ✅ Dummy Reminder Loop (to avoid import error)
async def reminder_loop():
    return
