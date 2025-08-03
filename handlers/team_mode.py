from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio, json, os, random

router = Router()
DATA_FILE = "database/football_data.json"

# ✅ Load/Save
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"teamA": [], "teamB": [], "referee": None, "score": {"A":0,"B":0}, "round":1, "ball": None, "votes": {}}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ✅ Create Team (Referee assigns)
@router.message(Command("create_team"))
async def create_team(msg: Message):
    data = load_data()
    if data["referee"] is None:
        data["referee"] = msg.from_user.id
        save_data(data)
        return await msg.answer("✅ You are now the Referee! Use /add_player to add members.")

    await msg.answer("❌ Referee already exists!")

# ✅ Add Player
@router.message(Command("add_player"))
async def add_player(msg: Message):
    data = load_data()
    if msg.from_user.id != data["referee"]:
        return await msg.answer("❌ Only referee can add players!")

    if msg.reply_to_message:
        user = msg.reply_to_message.from_user
    else:
        parts = msg.text.split()
        if len(parts) < 2:
            return await msg.answer("⚠ Usage: /add_player @username (or reply)")
        user = msg.entities[1].user if msg.entities and msg.entities[1].user else None

    if not user:
        return await msg.answer("❌ Invalid user!")

    if user.id == data["referee"]:
        return await msg.answer("🚫 Referee cannot join the game!")

    if user.username in data["teamA"] or user.username in data["teamB"]:
        return await msg.answer("⚠ Player already added!")

    # Balance check
    if len(data["teamA"]) <= len(data["teamB"]):
        data["teamA"].append(user.username or user.full_name)
        team = "A"
    else:
        data["teamB"].append(user.username or user.full_name)
        team = "B"

    save_data(data)
    await msg.answer(f"✅ Added **{user.full_name}** to Team {team}")

# ✅ Remove Player A
@router.message(Command("remove_player_A"))
async def remove_player_a(msg: Message):
    data = load_data()
    if msg.from_user.id != data["referee"]:
        return await msg.answer("❌ Only referee can remove players!")
    parts = msg.text.split()
    if len(parts) < 2 or not parts[1].isdigit():
        return await msg.answer("⚠ Usage: /remove_player_A <number>")
    idx = int(parts[1]) - 1
    if idx < 0 or idx >= len(data["teamA"]):
        return await msg.answer("❌ Invalid player number in Team A")
    player = data["teamA"].pop(idx)
    save_data(data)
    await msg.answer(f"🗑 Removed **{player}** from Team A")

# ✅ Remove Player B
@router.message(Command("remove_player_B"))
async def remove_player_b(msg: Message):
    data = load_data()
    if msg.from_user.id != data["referee"]:
        return await msg.answer("❌ Only referee can remove players!")
    parts = msg.text.split()
    if len(parts) < 2 or not parts[1].isdigit():
        return await msg.answer("⚠ Usage: /remove_player_B <number>")
    idx = int(parts[1]) - 1
    if idx < 0 or idx >= len(data["teamB"]):
        return await msg.answer("❌ Invalid player number in Team B")
    player = data["teamB"].pop(idx)
    save_data(data)
    await msg.answer(f"🗑 Removed **{player}** from Team B")

# ✅ Start Round (Referee only)
@router.message(Command("start_round"))
async def start_round(msg: Message):
    data = load_data()
    if msg.from_user.id != data["referee"]:
        return await msg.answer("❌ Only referee can start rounds!")

    current_round = data["round"]
    if current_round > 3:
        return await msg.answer("🏆 All 3 rounds completed!")

    if not data["teamA"] or not data["teamB"]:
        return await msg.answer("⚠ Both teams must have players to start!")

    data["ball"] = random.choice(data["teamA"] + data["teamB"])
    save_data(data)
    await msg.answer(f"🔔 **Round {current_round} STARTED!**\n⚽ Ball with: @{data['ball']}")

# ✅ Score Command
@router.message(Command("score"))
async def score(msg: Message):
    data = load_data()
    round_text = "FINAL ROUND" if data["round"] == 3 else f"Round {data['round']}"
    score_text = f"""
🏆 **SCOREBOARD**
Team A: {data['score']['A']}
Team B: {data['score']['B']}
Current: {round_text}
"""
    await msg.answer(score_text)

# ✅ Time Command
@router.message(Command("time"))
async def time_alert(msg: Message):
    data = load_data()
    if msg.from_user.id != data["referee"]:
        return await msg.answer("❌ Only referee can send time alerts!")

    alerts = [
        ("⏰ 15 MINUTES LEFT!", "https://media.giphy.com/media/26AHONQ79FdWZhAI0/giphy.gif"),
        ("⏰ 10 MINUTES LEFT!", "https://media.giphy.com/media/l0HlQ7LRal7hytzGM/giphy.gif"),
        ("⏰ 5 MINUTES LEFT!", "https://media.giphy.com/media/xT0xeJpnrWC4XWblEk/giphy.gif"),
        ("⏰ 1 MINUTE LEFT!", "https://media.giphy.com/media/3o6Zt481isNVuQI1l6/giphy.gif")
    ]
    for text, gif in alerts:
        await msg.answer_animation(gif, caption=text)
        await asyncio.sleep(3)

# ✅ Kick Command (Player+GK choose number)
@router.message(Command("kick"))
async def kick(msg: Message):
    data = load_data()
    if msg.from_user.username != data["ball"]:
        return await msg.answer("⚽ You don't have the ball!")

    numbers = list(range(1,6))
    btns = InlineKeyboardBuilder()
    for n in numbers:
        btns.button(text=str(n), callback_data=f"kick:{n}")
    await msg.answer("🎯 Choose your kick number (1-5)", reply_markup=btns.as_markup())

# ✅ PASS Command
@router.message(Command("pass"))
async def pass_cmd(msg: Message):
    data = load_data()
    current = msg.from_user.username
    if current != data["ball"]:
        return await msg.answer("⚽ You don't have the ball!")

    team = "A" if current in data["teamA"] else "B"
    players = data["teamA"] if team=="A" else data["teamB"]
    idx = players.index(current)
    nearby = [p for i,p in enumerate(players) if abs(i-idx)==1]
    far = [p for i,p in enumerate(players) if abs(i-idx)>1]

    btns = InlineKeyboardBuilder()
    for p in nearby:
        btns.button(text=f"LOB → {p}", callback_data=f"pass:lob:{p}")
    for p in far:
        btns.button(text=f"LONG → {p}", callback_data=f"pass:long:{p}")
    await msg.answer("🤝 Choose pass type & player", reply_markup=btns.as_markup())

# ✅ End Match (RESET EVERYTHING)
@router.message(Command("end_match"))
async def end_match(msg: Message):
    data = load_data()
    if msg.from_user.id != data["referee"]:
        return await msg.answer("❌ Only referee can end the match!")

    save_data({"teamA": [], "teamB": [], "referee": None, "score": {"A":0,"B":0}, "round":1, "ball": None, "votes": {}})
    await msg.answer("🛑 Match ended!\n✅ Teams, scores & referee cleared. Ready for a new game.")
