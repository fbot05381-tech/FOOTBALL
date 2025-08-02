import os, random, asyncio, datetime
from aiogram import Router, types, F
from aiogram.filters import Command
from utils.db import load_json, save_json

router = Router()
DATA_DIR = "database"
TOURNAMENT_FILE = os.path.join(DATA_DIR, "tournament.json")

def init_tournament():
    return {
        "owner": None,
        "total_teams": 0,
        "players_per_team": 0,
        "registered_teams": {},
        "matches": [],
        "points_table": {},
        "tournament_started": False
    }

# ✅ Background Task for Reminders
async def reminder_loop(bot):
    while True:
        await asyncio.sleep(60)
        data = load_json(TOURNAMENT_FILE)
        if not data.get("matches"):
            continue

        now = datetime.datetime.now().strftime("%H:%M")
        for m in data["matches"]:
            if m.get("time") and not m.get("reminded"):
                match_time = m["time"]
                hour, minute = map(int, match_time.split(":"))
                dt_match = datetime.datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
                diff = (dt_match - datetime.datetime.now()).total_seconds() / 60

                if 4 <= diff <= 6:  # 5 min before
                    t1_captain = data["registered_teams"][m["team1"]]["captain"]
                    t2_captain = data["registered_teams"][m["team2"]]["captain"]

                    text = f"⏰ <b>Match Reminder</b>\n\n⚽ {m['team1']} vs {m['team2']} starting in 5 minutes!\n\n👑 Captains: @{t1_captain['name']} vs @{t2_captain['name']}"
                    await bot.send_message(m["chat_id"], text, parse_mode="HTML")
                    m["reminded"] = True
                    save_json(TOURNAMENT_FILE, data)

@router.callback_query(F.data == "tournament_mode")
async def tournament_mode(cb: types.CallbackQuery):
    save_json(TOURNAMENT_FILE, init_tournament())
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="👑 I'm the Owner", callback_data="be_owner")]
    ])
    await cb.message.answer("🏆 Tournament Mode selected!\nChoose an Owner to organize tournament:", reply_markup=kb)

@router.callback_query(F.data == "be_owner")
async def be_owner(cb: types.CallbackQuery):
    data = load_json(TOURNAMENT_FILE)
    if data.get("owner"):
        return await cb.answer("Owner already selected!", show_alert=True)
    data["owner"] = cb.from_user.id
    save_json(TOURNAMENT_FILE, data)
    await cb.message.edit_text(f"👑 {cb.from_user.full_name} is now Tournament Owner!\nUse /create_tournament")

@router.message(Command("create_tournament"))
async def create_tournament(msg: types.Message):
    data = load_json(TOURNAMENT_FILE)
    if msg.from_user.id != data.get("owner"):
        return await msg.answer("Only the Owner can create tournament.")

    await msg.answer("✅ Tournament created!\nNow set total teams using /total_team 4-10")

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
    await msg.answer(f"👥 Players per team set to {count}\nNow teams can register using /register_team")

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
    data["points_table"][team_name] = {"played": 0, "win": 0, "loss": 0, "points": 0}

    save_json(TOURNAMENT_FILE, data)
    await msg.answer(f"✅ Team '{team_name}' registered with Captain {captain_name}")

@router.message(Command("start_tournament"))
async def start_tournament(msg: types.Message):
    data = load_json(TOURNAMENT_FILE)
    if msg.from_user.id != data.get("owner"):
        return await msg.answer("Only Owner can start tournament.")
    if data["tournament_started"]:
        return await msg.answer("Tournament already started!")

    if len(data["registered_teams"]) != data["total_teams"]:
        return await msg.answer("⚠️ All teams must be registered before starting.")

    teams = list(data["registered_teams"].keys())
    matches = []
    for i in range(len(teams)):
        for j in range(i+1, len(teams)):
            matches.append({"team1": teams[i], "team2": teams[j], "played": False, "chat_id": msg.chat.id})

    random.shuffle(matches)
    data["matches"] = matches
    data["tournament_started"] = True
    save_json(TOURNAMENT_FILE, data)

    match_list = "\n".join([f"⚽ {m['team1']} vs {m['team2']}" for m in matches])
    await msg.answer(f"🏆 Tournament Started!\n\n📅 Match Schedule:\n{match_list}")

@router.message(Command("set_match_time"))
async def set_match_time(msg: types.Message):
    data = load_json(TOURNAMENT_FILE)
    if msg.from_user.id != data.get("owner"):
        return await msg.answer("Only Owner can set match times.")

    parts = msg.text.split()
    if len(parts) != 4:
        return await msg.answer("Usage: /set_match_time TeamA TeamB 18:30")

    team1, team2, time_str = parts[1], parts[2], parts[3]
    for m in data["matches"]:
        if {m["team1"], m["team2"]} == {team1, team2}:
            m["time"] = time_str
            m["reminded"] = False
            save_json(TOURNAMENT_FILE, data)
            return await msg.answer(f"⏰ Match time set: {team1} vs {team2} at {time_str}")

    await msg.answer("Match not found!")

@router.message(Command("points_table"))
async def points_table(msg: types.Message):
    data = load_json(TOURNAMENT_FILE)
    if not data.get("points_table"):
        return await msg.answer("No tournament data available.")

    table = "🏆 <b>Points Table</b>\n\n"
    for team, stats in sorted(data["points_table"].items(), key=lambda x: x[1]["points"], reverse=True):
        table += f"{team} - {stats['points']} pts (W:{stats['win']} L:{stats['loss']} P:{stats['played']})\n"

    await msg.answer(table, parse_mode="HTML")
