from telegram import Update
from telegram.ext import ContextTypes
from utils.database import db

# ✅ Tournament Mode Button
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

# ✅ Create Tournament
async def create_tournament(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    db["tournaments"][chat_id] = {
        "owner": user_id,
        "teams": {},
        "total_teams": 0,
        "team_size": (0, 0),
        "status": "created"
    }

    await update.message.reply_text("🏆 Tournament Created!\nNow set total teams using /total_team <number>")

# ✅ Set Total Teams
async def total_team(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    try:
        total = int(context.args[0])
    except:
        await update.message.reply_text("❌ Usage: /total_team <number>")
        return

    db["tournaments"][chat_id]["total_teams"] = total
    await update.message.reply_text(f"✅ Total Teams set to {total}. Now set team members using /team_members <min>-<max>")

# ✅ Set Team Members
async def team_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    try:
        min_max = context.args[0].split("-")
        min_players = int(min_max[0])
        max_players = int(min_max[1])
    except:
        await update.message.reply_text("❌ Usage: /team_members <min>-<max>")
        return

    db["tournaments"][chat_id]["team_size"] = (min_players, max_players)
    db["tournaments"][chat_id]["status"] = "registration"
    await update.message.reply_text(f"✅ Team members set ({min_players}-{max_players}).\nRegistration started!\nCaptains use /register_team <Team Name>")

# ✅ Register Team
async def register_team(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user

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

    # Check if user already in any team
    for t in db["tournaments"][chat_id]["teams"].values():
        if user.id in t["players"]:
            await update.message.reply_text("❌ You are already in another team.")
            return

    team["players"].append(user.id)
    await update.message.reply_text(f"✅ {user.first_name} joined Team '{team_name}' ({len(team['players'])}/{max_players})")
