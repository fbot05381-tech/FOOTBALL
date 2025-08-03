from aiogram import Router, F
from aiogram.types import Message, InputSticker
from utils.db import get_match_data, save_match_data, reset_match_data
import random, asyncio, time

router = Router()

# ⏱️ Rate Limit Storage
last_command_time = {}
last_score_time_group = {}

# ✅ Default Sticker ID (Telegram Animated Trophy)
DEFAULT_STICKER = "CAACAgIAAxkBAAEBxJxnk_TROPHY_STICKER"

def check_rate_limit(user_id, chat_id, cmd, limit):
    now = time.time()
    if cmd == "score":
        global last_score_time_group
        if chat_id in last_score_time_group and now - last_score_time_group[chat_id] < limit:
            return False
        last_score_time_group[chat_id] = now
        return True
    else:
        if user_id in last_command_time and now - last_command_time[user_id] < limit:
            return False
        last_command_time[user_id] = now
        return True

# ✅ Create Team
@router.message(F.text == "/create_team")
async def create_team(msg: Message):
    if not check_rate_limit(msg.from_user.id, msg.chat.id, "create", 10):
        await msg.answer("⏳ Please wait 10 seconds before using another command.")
        return

    data = get_match_data()
    data["teams"] = {"A": [], "B": []}
    data["referee_id"] = msg.from_user.id
    data["status"] = "waiting"
    data["round"] = 0
    data["start_time"] = None
    data["score"] = {"A":0, "B":0}
    data["player_stats"] = {}
    save_match_data(data)

    await msg.answer("🎮 Match setup created!\n\nPlayers, type /join_football to join Team A or Team B.")

    async def join_alerts():
        await asyncio.sleep(60)
        await msg.answer("⏳ 1 Minute left! Type /join_football to join the match.")
        await asyncio.sleep(30)
        await msg.answer("⏳ 30 Seconds left! Last chance to join with /join_football.")
        await asyncio.sleep(30)
        await finalize_teams(msg)

    asyncio.create_task(join_alerts())

# ✅ Join Football
@router.message(F.text == "/join_football")
async def join_football(msg: Message):
    if not check_rate_limit(msg.from_user.id, msg.chat.id, "join", 10):
        await msg.answer("⏳ Please wait 10 seconds before using another command.")
        return

    data = get_match_data()
    if data.get("status") != "waiting":
        await msg.answer("⚠️ No active match to join.")
        return

    username = msg.from_user.full_name
    if username in data['teams']['A'] or username in data['teams']['B']:
        await msg.answer("✅ You already joined a team!")
        return

    if len(data['teams']['A']) <= len(data['teams']['B']):
        data['teams']['A'].append(username)
        team = "A"
    else:
        data['teams']['B'].append(username)
        team = "B"

    save_match_data(data)
    await msg.answer(f"✅ {username} joined Team {team}!")

# ✅ Finalize Teams
async def finalize_teams(msg: Message):
    data = get_match_data()
    if not data['teams']['A'] or not data['teams']['B']:
        await msg.answer("⚠️ Not enough players to start the match.")
        return

    if data['teams']['A']:
        data['captain_A'] = random.choice(data['teams']['A'])
        data['gk_A'] = random.choice(data['teams']['A'])
    if data['teams']['B']:
        data['captain_B'] = random.choice(data['teams']['B'])
        data['gk_B'] = random.choice(data['teams']['B'])

    save_match_data(data)

    text = get_team_text(data)
    pin_msg = await msg.answer(text, parse_mode="HTML")
    try:
        await msg.chat.pin_message(pin_msg.message_id)
    except:
        pass

    await msg.answer("🏁 Referee can now start the match using /start_match.")

# ✅ Helper: Team Text
def get_team_text(data):
    text = "✅ Teams Locked!\n\n"
    text += "🔵 <b>Team A:</b>\n"
    for p in data['teams']['A']:
        tag = ""
        if p == data.get('captain_A'): tag = " (C)"
        if p == data.get('gk_A'): tag += " (GK)"
        text += f"• {p}{tag}\n"

    text += "\n🔴 <b>Team B:</b>\n"
    for p in data['teams']['B']:
        tag = ""
        if p == data.get('captain_B'): tag = " (C)"
        if p == data.get('gk_B'): tag += " (GK)"
        text += f"• {p}{tag}\n"
    return text

# ✅ Show Teams
@router.message(F.text == "/show_teams")
async def show_teams(msg: Message):
    if not check_rate_limit(msg.from_user.id, msg.chat.id, "show_teams", 10):
        await msg.answer("⏳ Please wait 10 seconds before using another command.")
        return

    data = get_match_data()
    if not data.get("teams"):
        await msg.answer("⚠️ No teams created yet.")
        return

    text = get_team_text(data)
    await msg.answer(text, parse_mode="HTML")

# ✅ Start Match (Referee Only)
@router.message(F.text == "/start_match")
async def start_match(msg: Message):
    if not check_rate_limit(msg.from_user.id, msg.chat.id, "start_match", 10):
        await msg.answer("⏳ Please wait 10 seconds before using another command.")
        return

    data = get_match_data()
    if msg.from_user.id != data.get("referee_id"):
        await msg.answer("⚠️ Only referee can start the match.")
        return

    data["status"] = "ongoing"
    data["round"] = 1
    data["start_time"] = time.time()
    save_match_data(data)

    await msg.answer("🏆 Match Started! Round 1 begins now!")

# ✅ End Match
@router.message(F.text == "/end_match")
async def end_match(msg: Message):
    if not check_rate_limit(msg.from_user.id, msg.chat.id, "end_match", 10):
        await msg.answer("⏳ Please wait 10 seconds before using another command.")
        return

    data = get_match_data()
    if msg.from_user.id != data.get("referee_id"):
        await msg.answer("⚠️ Only referee can end the match.")
        return

    if not data.get("teams"):
        await msg.answer("⚠️ No active match found.")
        return

    # Duration
    duration_text = ""
    if data.get("start_time"):
        duration = int(time.time() - data["start_time"])
        mins = duration // 60
        secs = duration % 60
        duration_text = f"\n⏱️ Match Duration: <b>{mins}m {secs}s</b>"

    text = "🏁 <b>FINAL MATCH SUMMARY</b>\n\n"
    text += get_team_text(data)
    text += f"\n\n🔵 Team A: {data['score']['A']}  |  🔴 Team B: {data['score']['B']}"
    text += duration_text

    await msg.answer(text, parse_mode="HTML")
    reset_match_data()
    await msg.answer("✅ Match ended and all match data has been reset!")

# ✅ Show Score (30s Group-wide Limit) + Sticker Combo
@router.message(F.text == "/score")
async def show_score(msg: Message):
    if not check_rate_limit(msg.from_user.id, msg.chat.id, "score", 30):
        await msg.answer("⏳ /score can only be used once every 30 seconds for the whole group.")
        return

    data = get_match_data()
    if not data.get("teams"):
        await msg.answer("⚠️ No active match.")
        return

    text = "📊 <b>Current Scoreboard</b>\n\n"
    text += f"🔵 Team A: <b>{data['score']['A']}</b>\n"
    text += f"🔴 Team B: <b>{data['score']['B']}</b>\n\n"

    if data.get("player_stats"):
        text += "👥 <b>Player Stats:</b>\n"
        for player, stats in data['player_stats'].items():
            text += f"• {player}: ⚽ {stats.get('goals',0)}  🎯 {stats.get('assists',0)}\n"

    # 🔥 Send Sticker + Scoreboard Combo
    try:
        await msg.answer_sticker(DEFAULT_STICKER)
    except:
        pass
    await msg.answer(text, parse_mode="HTML")
