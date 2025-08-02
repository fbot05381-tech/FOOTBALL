import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Chat
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# ✅ तुम्हारा Token
TOKEN = "7496362823:AAHpnck9YF3HmaPU7lYIOqKMD1TfpHirUmE"

# ✅ In-Memory DB
db = {"tournaments": {}}

# ✅ Import handlers
from game.team_mode import handle_team_mode, create_team
from game.tournament import (
    handle_tournament_mode,
    total_team,
    team_members
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Group check
async def is_group(update: Update):
    return update.effective_chat.type in [Chat.GROUP, Chat.SUPERGROUP]

# ✅ /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_group(update): return
    await update.message.reply_text("✅ Football Bot Active! Use /start_football")

# ✅ /start_football
async def start_football(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_group(update): return
    keyboard = [
        [InlineKeyboardButton("🏆 Tournament Mode", callback_data="tournament_mode")],
        [InlineKeyboardButton("👥 Team Mode", callback_data="team_mode")],
    ]
    await update.message.reply_text("⚽ Choose Game Mode:", reply_markup=InlineKeyboardMarkup(keyboard))

# ✅ Button Callback
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.message.chat.type not in [Chat.GROUP, Chat.SUPERGROUP]:
        await query.answer(); return
    await query.answer()

    if query.data == "tournament_mode":
        await handle_tournament_mode(query)
    elif query.data == "team_mode":
        await handle_team_mode(query)

# ✅ Create Tournament
async def create_tournament(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    db["tournaments"][chat_id] = {
        "owner": update.effective_user.id,
        "teams": {},
        "total_teams": 0,
        "team_size": (0, 0),
        "status": "created"
    }
    await update.message.reply_text("🏆 Tournament Created!\nUse /total_team <number>")

# ✅ Register Team
async def register_team(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user

    if chat_id not in db["tournaments"]:
        await update.message.reply_text("❌ No tournament created.")
        return

    if db["tournaments"][chat_id]["status"] != "registration":
        await update.message.reply_text("❌ Registration not open.")
        return

    if len(context.args) == 0:
        await update.message.reply_text("❌ Usage: /register_team <Team Name>")
        return

    team_name = " ".join(context.args)

    if team_name in db["tournaments"][chat_id]["teams"]:
        await update.message.reply_text("❌ Team name already taken.")
        return

    if len(db["tournaments"][chat_id]["teams"]) >= db["tournaments"][chat_id]["total_teams"]:
        await update.message.reply_text("❌ All team slots are full.")
        return

    db["tournaments"][chat_id]["teams"][team_name] = {
        "captain": user.id,
        "players": [user.id]
    }

    await update.message.reply_text(f"✅ Team '{team_name}' registered!\nCaptain: {user.first_name}\nPlayers can join using /join_team {team_name}")

# ✅ Join Team
async def join_team(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user

    if chat_id not in db["tournaments"]:
        await update.message.reply_text("❌ No tournament created.")
        return

    if db["tournaments"][chat_id]["status"] != "registration":
        await update.message.reply_text("❌ Registration not open.")
        return

    if len(context.args) == 0:
        await update.message.reply_text("❌ Usage: /join_team <Team Name>")
        return

    team_name = " ".join(context.args)

    if team_name not in db["tournaments"][chat_id]["teams"]:
        await update.message.reply_text("❌ No such team registered.")
        return

    min_players, max_players = db["tournaments"][chat_id]["team_size"]
    team = db["tournaments"][chat_id]["teams"][team_name]

    if user.id in team["players"]:
        await update.message.reply_text("❌ You are already in this team.")
        return

    if len(team["players"]) >= max_players:
        await update.message.reply_text("❌ Team is already full.")
        return

    # Check if user already in another team
    for t in db["tournaments"][chat_id]["teams"].values():
        if user.id in t["players"]:
            await update.message.reply_text("❌ You are already in another team.")
            return

    team["players"].append(user.id)
    await update.message.reply_text(f"✅ {user.first_name} joined Team '{team_name}' ({len(team['players'])}/{max_players})")

# ✅ Main
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    # 🔹 Start commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("start_football", start_football))
    app.add_handler(CallbackQueryHandler(button_handler))

    # 🔹 Tournament commands
    app.add_handler(CommandHandler("create_tournament", create_tournament))
    app.add_handler(CommandHandler("total_team", total_team))
    app.add_handler(CommandHandler("team_members", team_members))
    app.add_handler(CommandHandler("register_team", register_team))  # ✅ Fixed position
    app.add_handler(CommandHandler("join_team", join_team))          # ✅ Fixed position

    # 🔹 Team mode
    app.add_handler(CommandHandler("create_team", create_team))

    print("✅ Football Bot Running...")
    app.run_polling(allowed_updates=["message", "chat_member", "callback_query"])
