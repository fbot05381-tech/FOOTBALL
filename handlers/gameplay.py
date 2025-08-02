import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, CallbackContext
from config import TEAMS_FILE, GOAL_GIF, PASS_GIF, DEFENSIVE_GIF, STEAL_GIF, CELEBRATION_GIF, SAD_GIF
from handlers.utils import load_json, save_json, get_user_team, update_player_stat, get_mvp

# ✅ Start Match (Referee Only)
async def start_match(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    teams = load_json(TEAMS_FILE)

    if str(chat_id) not in teams:
        await update.message.reply_text("⚠️ No active game.")
        return

    game = teams[str(chat_id)]
    if update.effective_user.id != game["referee"]:
        await update.message.reply_text("⚠️ Only referee can start the match!")
        return

    await update.message.reply_text("🏁 Match Starting! 3 Rounds of 15 mins each.")
    await coin_toss(update, context)

# ✅ Coin Toss for first ball
async def coin_toss(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    teams = load_json(TEAMS_FILE)[str(chat_id)]
    capA = teams["team_A"]["captain"]
    capB = teams["team_B"]["captain"]

    if not capA or not capB:
        await update.message.reply_text("⚠️ Both teams need captains first!")
        return

    toss_choice = random.choice(["Heads", "Tails"])
    winner = random.choice([capA, capB])

    teams["ball"] = winner
    save_json(TEAMS_FILE, load_json(TEAMS_FILE))

    await update.message.reply_text(
        f"🪙 Coin Toss: {toss_choice}\n⚽ Ball goes to Player {winner}!"
    )
    await show_actions(update, winner)

# ✅ Show Actions to Player with Ball
async def show_actions(update: Update, player_id):
    keyboard = [
        [InlineKeyboardButton("🥅 KICK", callback_data=f"kick_{player_id}")],
        [InlineKeyboardButton("🛡 DEFENSIVE", callback_data=f"defensive_{player_id}")],
        [InlineKeyboardButton("🔄 PASS", callback_data=f"pass_{player_id}")]
    ]
    await update.message.reply_text(f"⚽ Player {player_id}, your move:", reply_markup=InlineKeyboardMarkup(keyboard))

# ✅ Handle KICK
async def handle_kick(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    player_id = int(query.data.split("_")[1])
    chat_id = query.message.chat_id

    team = get_user_team(chat_id, player_id)
    teams = load_json(TEAMS_FILE)
    game = teams[str(chat_id)]

    gk_id = game["team_B"]["gk"] if team == "A" else game["team_A"]["gk"]

    # ✅ Penalty shootout
    player_num = random.randint(1, 5)
    gk_num = random.randint(1, 5)

    if player_num == gk_num:
        await query.message.reply_animation(SAD_GIF, caption=f"🧤 Goalkeeper {gk_id} SAVED the goal!")
    else:
        await query.message.reply_animation(GOAL_GIF, caption=f"🥅 GOAL by Player {player_id}!")
        update_player_stat(player_id, "goals")

    save_json(TEAMS_FILE, teams)

# ✅ Handle DEFENSIVE
async def handle_defensive(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    player_id = int(query.data.split("_")[1])

    # Opponent chance to steal
    if random.random() < 0.3:
        opponent = random.randint(1000, 9999)  # Dummy opponent id for now
        await query.message.reply_animation(STEAL_GIF, caption=f"❌ Ball stolen by Player {opponent}")
        update_player_stat(opponent, "steals")
    else:
        await query.message.reply_animation(DEFENSIVE_GIF, caption=f"🛡 Player {player_id} moves forward defensively.")

    update_player_stat(player_id, "steals")

# ✅ Handle PASS
async def handle_pass(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    player_id = int(query.data.split("_")[1])

    teammate = random.randint(1000, 9999)  # Dummy teammate id for now
    await query.message.reply_animation(PASS_GIF, caption=f"🔄 Player {player_id} passes to Player {teammate}")
    update_player_stat(player_id, "passes")

# ✅ Show MVP after match
async def show_mvp(update: Update, context: CallbackContext):
    mvp = get_mvp()
    if mvp:
        await update.message.reply_animation(CELEBRATION_GIF, caption=f"🏆 MVP of the Match: Player {mvp}")
    else:
        await update.message.reply_text("No MVP found.")

# ✅ Register Handlers
def register_handlers(app):
    app.add_handler(CommandHandler("start_match", start_match))
    app.add_handler(CallbackQueryHandler(handle_kick, pattern="^kick_"))
    app.add_handler(CallbackQueryHandler(handle_defensive, pattern="^defensive_"))
    app.add_handler(CallbackQueryHandler(handle_pass, pattern="^pass_"))
    app.add_handler(CommandHandler("mvp", show_mvp))
