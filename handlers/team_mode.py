import random, asyncio
from aiogram import Router, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from utils.db import read_db, update_db

router = Router()
active_matches = {}

# ✅ Create Teams
@router.message(Command("create_team"))
async def create_team(msg: Message):
    chat_id = str(msg.chat.id)
    db = read_db()

    db[chat_id] = {
        "teamA": [],
        "teamB": [],
        "captains": {},
        "goalkeepers": {},
        "referee": msg.from_user.id,
        "current_ball": None,
        "cards": {},
        "round": 0
    }
    update_db(chat_id, db[chat_id])
    await msg.answer(f"✅ Teams created!\n🎟️ Referee: {msg.from_user.mention_html()}\nPlayers use /join_football to join.", parse_mode="HTML")

# ✅ Join Football
@router.message(Command("join_football"))
async def join_football(msg: Message):
    chat_id = str(msg.chat.id)
    db = read_db()
    user = msg.from_user.id

    if chat_id not in db:
        await msg.answer("❌ No active match. Use /create_team first.")
        return

    # 🚫 Referee cannot join game
    if user == db[chat_id]["referee"]:
        await msg.answer("⚠️ Referee cannot join the match!")
        return

    if user in db[chat_id]["teamA"] or user in db[chat_id]["teamB"]:
        await msg.answer("⚠️ You already joined a team!")
        return

    # Balance Teams
    if len(db[chat_id]["teamA"]) <= len(db[chat_id]["teamB"]):
        db[chat_id]["teamA"].append(user)
        team = "A"
    else:
        db[chat_id]["teamB"].append(user)
        team = "B"

    update_db(chat_id, db[chat_id])
    await msg.answer(f"✅ {msg.from_user.mention_html()} joined FOOTBALL TEAM {team}", parse_mode="HTML")

# ✅ Start Round (Referee Only)
@router.message(Command("start_round"))
async def start_round(msg: Message):
    chat_id = str(msg.chat.id)
    db = read_db()

    if chat_id not in db:
        await msg.answer("❌ No active match.")
        return

    if msg.from_user.id != db[chat_id]["referee"]:
        await msg.answer("⚠️ Only referee can start a round!")
        return

    db[chat_id]["round"] += 1
    update_db(chat_id, db[chat_id])

    await msg.answer(f"🚩 Round {db[chat_id]['round']} Started!\n⚽ Referee controls the match.")

# ✅ KICK Command
@router.message(Command("kick"))
async def kick(msg: Message):
    chat_id = str(msg.chat.id)
    db = read_db()

    if chat_id not in db:
        await msg.answer("❌ No active match.")
        return

    user = msg.from_user.mention_html()
    db_data = db[chat_id]

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=str(i), callback_data=f"kick_num:{i}:{msg.from_user.id}")]
        for i in range(1, 6)
    ])
    await msg.answer(f"⚽ {user} is attempting a KICK!\nSelect your number (1-5)", parse_mode="HTML", reply_markup=keyboard)

# ✅ Handle KICK Number
@router.callback_query(lambda c: c.data.startswith("kick_num:"))
async def handle_kick_number(callback: types.CallbackQuery):
    _, num, player_id = callback.data.split(":")
    num = int(num)
    chat_id = str(callback.message.chat.id)
    db = read_db()

    gk_num = random.randint(1, 5)
    if num == gk_num:
        await callback.message.answer(f"🧤 GK saved the GOAL!\nPlayer ID: {player_id}")
    else:
        await callback.message.answer(f"🥅 GOAL Scored by Player ID: {player_id}")

# ✅ PASS Command
@router.message(Command("pass"))
async def pass_ball(msg: Message):
    chat_id = str(msg.chat.id)
    db = read_db()

    if chat_id not in db:
        await msg.answer("❌ No active match.")
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 LOB PASS", callback_data="pass_type:lob")],
        [InlineKeyboardButton(text="🎯 LONG PASS", callback_data="pass_type:long")]
    ])
    await msg.answer("Choose PASS type:", reply_markup=keyboard)

# ✅ Handle PASS Type
@router.callback_query(lambda c: c.data.startswith("pass_type:"))
async def handle_pass_type(callback: types.CallbackQuery):
    chat_id = str(callback.message.chat.id)
    db = read_db()

    pass_type = callback.data.split(":")[1]
    players = db[chat_id]["teamA"] + db[chat_id]["teamB"]

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"Player {i+1}", callback_data=f"pass_player:{pid}")]
        for i, pid in enumerate(players)
    ])
    await callback.message.answer(f"Select a player for {pass_type.upper()} PASS:", reply_markup=keyboard)

# ✅ Handle PASS Player
@router.callback_query(lambda c: c.data.startswith("pass_player:"))
async def handle_pass_player(callback: types.CallbackQuery):
    player_id = callback.data.split(":")[1]
    await callback.message.answer(f"✅ Ball passed to Player {player_id}")

# ✅ RED CARD
@router.message(Command("red_card"))
async def red_card(msg: Message):
    chat_id = str(msg.chat.id)
    db = read_db()
    user = msg.reply_to_message.from_user.id if msg.reply_to_message else None

    if not user:
        await msg.answer("⚠️ Reply to a player's message to give a RED CARD.")
        return

    if user in db[chat_id]["teamA"]:
        db[chat_id]["teamA"].remove(user)
    if user in db[chat_id]["teamB"]:
        db[chat_id]["teamB"].remove(user)

    db[chat_id]["cards"][user] = "RED"
    update_db(chat_id, db[chat_id])
    await msg.answer(f"🟥 RED CARD!\nPlayer {msg.reply_to_message.from_user.mention_html()} removed from match!", parse_mode="HTML")

# ✅ YELLOW CARD
@router.message(Command("yellow_card"))
async def yellow_card(msg: Message):
    chat_id = str(msg.chat.id)
    db = read_db()
    user = msg.reply_to_message.from_user.id if msg.reply_to_message else None

    if not user:
        await msg.answer("⚠️ Reply to a player's message to give a YELLOW CARD.")
        return

    db[chat_id]["cards"][user] = "YELLOW"
    update_db(chat_id, db[chat_id])
    await msg.answer(f"🟨 YELLOW CARD to {msg.reply_to_message.from_user.mention_html()}", parse_mode="HTML")
