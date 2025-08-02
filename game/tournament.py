from telegram import Update
from telegram.ext import ContextTypes
from utils.database import db

# ✅ Tournament Mode Button Handler
async def handle_tournament_mode(query):
    chat_id = query.message.chat_id
    db["tournaments"][chat_id] = {
        "owner": query.from_user.id,
        "teams": {},
        "total_teams": 0,
        "team_size": (0, 0),
        "status": "created"
    }
    await query.message.reply_text("🏆 Tournament Mode selected!\nUse /create_tournament to start.")

# ✅ Create Tournament Command
async def create_tournament(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    if chat_id not in db["tournaments"]:
        db["tournaments"][chat_id] = {}

    db["tournaments"][chat_id]["owner"] = user_id
    db["tournaments"][chat_id]["teams"] = {}
    db["tournaments"][chat_id]["status"] = "created"

    await update.message.reply_text("🏆 Tournament Created!\nNow set total teams using /total_team <number>")

# ✅ Set Total Teams
async def total_team(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in db["tournaments"]:
        await update.message.reply_text("❌ First create a tournament using /create_tournament")
        return

    try:
        total = int(context.args[0])
    except:
        await update.message.reply_text("❌ Usage: /total_team <number>")
        return

    db["tournaments"][chat_id]["total_teams"] = total
    await update.message.reply_text(f"✅ Total Teams set to {total}. Now set team members using /team_members <min>-<max>")

# ✅ Set Team Members Limit
async def team_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in db["tournaments"]:
        await update.message.reply_text("❌ First create a tournament using /create_tournament")
        return

    try:
        min_max = context.args[0].split("-")
        min_players = int(min_max[0])
        max_players = int(min_max[1])
    except:
        await update.message.reply_text("❌ Usage: /team_members <min>-<max>")
        return

    db["tournaments"][chat_id]["team_size"] = (min_players, max_players)
    db["tournaments"][chat_id]["status"] = "registration"

    await update.message.reply_text(f"✅ Team members set ({min_players}-{max_players}).\nRegistration started!")
