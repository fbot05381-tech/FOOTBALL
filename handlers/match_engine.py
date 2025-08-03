from aiogram import Router, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio, random, time
from utils.db import load_db, save_db

router = Router()
COOLDOWN = {}

JOIN_TIME = 120  # 2 min join window
ROUND_TIME = 900  # 15 min round

def cooldown(user_id, cmd, sec):
    now = time.time()
    key = f"{user_id}_{cmd}"
    if key in COOLDOWN and now - COOLDOWN[key] < sec:
        return False
    COOLDOWN[key] = now
    return True

async def send_scoreboard(msg, match, bot):
    gif_list = [
        "https://media.giphy.com/media/3o7abKhOpu0NwenH3O/giphy.gif",
        "https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif"
    ]
    gif = random.choice(gif_list)
    team_a = "\n".join([f"{'(C)' if p==match.get('captainA') else ''}{'(GK)' if p==match.get('gkA') else ''} {p}" for p in match["teamA"]])
    team_b = "\n".join([f"{'(C)' if p==match.get('captainB') else ''}{'(GK)' if p==match.get('gkB') else ''} {p}" for p in match["teamB"]])
    text = f"""
📊 <b>SCOREBOARD</b>
🅰️ Team A: {match['score']['A']}
{team_a}

🅱️ Team B: {match['score']['B']}
{team_b}
    """
    sent = await msg.answer_animation(gif, caption=text, parse_mode="HTML")
    try:
        await bot.pin_chat_message(msg.chat.id, sent.message_id)
    except:
        pass

# ---- TEAM CREATION ----
@router.message(Command("create_team"))
async def create_team(msg: types.Message):
    db = load_db()
    chat_id = str(msg.chat.id)
    db["matches"][chat_id] = {"teamA": [], "teamB": [], "score": {"A": 0, "B": 0}, "referee": msg.from_user.id}
    save_db(db)
    await msg.answer("✅ Team creation started!\nPlayers join using /join_football")

    async def join_alerts():
        await asyncio.sleep(90)
        await msg.answer("⚠️ 30s left! Use /join_football")
        await asyncio.sleep(15)
        await msg.answer("⏳ 15s left! Final chance to /join_football")

    asyncio.create_task(join_alerts())
    await asyncio.sleep(JOIN_TIME)
    match = db["matches"][chat_id]
    if len(match["teamA"]) == len(match["teamB"]) and len(match["teamA"]) > 0:
        await msg.answer("✅ Teams are ready!")
        await send_scoreboard(msg, match, msg.bot)
    else:
        await msg.answer("❌ Teams not balanced. Add/remove players manually.")

@router.message(Command("join_football"))
async def join_football(msg: types.Message):
    db = load_db()
    chat_id = str(msg.chat.id)
    match = db["matches"].get(chat_id)
    if not match:
        await msg.answer("❌ No active team creation.")
        return
    username = msg.from_user.username or msg.from_user.first_name
    if username in match["teamA"] or username in match["teamB"]:
        return await msg.answer("⚠️ Already joined!")
    if len(match["teamA"]) <= len(match["teamB"]):
        match["teamA"].append(username)
    else:
        match["teamB"].append(username)
    save_db(db)
    await msg.answer(f"✅ {username} joined!")

# ---- PLAYER ADD/REMOVE ----
@router.message(Command("add_player"))
async def add_player(msg: types.Message):
    db = load_db()
    chat_id = str(msg.chat.id)
    match = db["matches"].get(chat_id)
    if not match: return await msg.answer("❌ No active match.")
    if msg.from_user.id != match["referee"]: return await msg.answer("⛔ Only referee can add players.")

    if msg.entities and len(msg.entities) > 1:
        username = msg.text.split()[1]
    elif msg.reply_to_message:
        username = msg.reply_to_message.from_user.username
    else:
        return await msg.answer("⚠️ Use /add_player @username or reply")

    if len(match["teamA"]) <= len(match["teamB"]):
        match["teamA"].append(username)
    else:
        match["teamB"].append(username)

    save_db(db)
    await msg.answer(f"✅ Player {username} added!")

@router.message(Command("remove_player_A"))
async def remove_player_a(msg: types.Message):
    db = load_db()
    chat_id = str(msg.chat.id)
    match = db["matches"].get(chat_id)
    if not match: return await msg.answer("❌ No active match.")
    if msg.from_user.id != match["referee"]: return await msg.answer("⛔ Only referee can remove players.")
    try:
        idx = int(msg.text.split()[1]) - 1
        removed = match["teamA"].pop(idx)
        save_db(db)
        await msg.answer(f"❌ Removed {removed} from Team A")
    except:
        await msg.answer("⚠️ Usage: /remove_player_A <number>")

@router.message(Command("remove_player_B"))
async def remove_player_b(msg: types.Message):
    db = load_db()
    chat_id = str(msg.chat.id)
    match = db["matches"].get(chat_id)
    if not match: return await msg.answer("❌ No active match.")
    if msg.from_user.id != match["referee"]: return await msg.answer("⛔ Only referee can remove players.")
    try:
        idx = int(msg.text.split()[1]) - 1
        removed = match["teamB"].pop(idx)
        save_db(db)
        await msg.answer(f"❌ Removed {removed} from Team B")
    except:
        await msg.answer("⚠️ Usage: /remove_player_B <number>")

# ---- REFEREE & CONTROL ----
@router.message(Command("set_referee"))
async def set_referee(msg: types.Message):
    db = load_db()
    chat_id = str(msg.chat.id)
    if chat_id not in db["matches"]:
        db["matches"][chat_id] = {"teamA": [], "teamB": [], "score": {"A":0,"B":0}}
    match = db["matches"][chat_id]

    if msg.entities and len(msg.entities) > 1:
        username = msg.text.split()[1]
    elif msg.reply_to_message:
        username = msg.reply_to_message.from_user.username
    else:
        return await msg.answer("⚠️ Use /set_referee @username or reply")

    match["referee"] = msg.from_user.id if msg.from_user.username == username else msg.reply_to_message.from_user.id
    save_db(db)
    await msg.answer(f"✅ Referee set to @{username}")

@router.message(Command("pause_game"))
async def pause_game(msg: types.Message):
    db = load_db()
    chat_id = str(msg.chat.id)
    match = db["matches"].get(chat_id)
    if not match: return await msg.answer("❌ No active match.")
    if msg.from_user.id != match.get("referee"): return await msg.answer("⛔ Only referee can pause.")
    match["paused"] = True
    save_db(db)
    pin = await msg.answer("⏸️ Game Paused! Referee can /resume_game")
    try:
        await msg.bot.pin_chat_message(msg.chat.id, pin.message_id)
    except:
        pass

@router.message(Command("resume_game"))
async def resume_game(msg: types.Message):
    db = load_db()
    chat_id = str(msg.chat.id)
    match = db["matches"].get(chat_id)
    if not match: return await msg.answer("❌ No active match.")
    if msg.from_user.id != match.get("referee"): return await msg.answer("⛔ Only referee can resume.")
    match["paused"] = False
    save_db(db)
    await msg.answer("▶️ Game Resumed!")

@router.message(Command("score"))
async def score(msg: types.Message):
    if not cooldown(msg.from_user.id, "score", 30): return await msg.answer("⏳ Wait 30 sec.")
    db = load_db()
    chat_id = str(msg.chat.id)
    if chat_id not in db["matches"]: return await msg.answer("❌ No active match.")
    await send_scoreboard(msg, db["matches"][chat_id], msg.bot)

@router.message(Command("end_match"))
async def end_match(msg: types.Message):
    db = load_db()
    chat_id = str(msg.chat.id)
    if chat_id in db["matches"]:
        del db["matches"][chat_id]
        save_db(db)
        await msg.answer("🏁 Match Ended! Stats not added.")
