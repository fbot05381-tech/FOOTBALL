from telegram import Update
from telegram.ext import CommandHandler, CallbackContext
from config import TEAMS_FILE
from handlers.utils import load_json, save_json, is_user_in_any_team

# ✅ Create Teams (Referee Only)
async def create_team(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    teams = load_json(TEAMS_FILE)

    if str(chat_id) not in teams:
        await update.message.reply_text("⚠️ First choose referee using /start_football")
        return

    game = teams[str(chat_id)]
    if update.effective_user.id != game["referee"]:
        await update.message.reply_text("⚠️ Only the referee can create teams!")
        return

    game["team_A"]["players"] = []
    game["team_B"]["players"] = []
    save_json(TEAMS_FILE, teams)

    await update.message.reply_text("✅ Teams created!\nPlayers use /join_A or /join_B to join.")

# ✅ Join Team A
async def join_A(update: Update, context: CallbackContext):
    await join_team(update, context, "A")

# ✅ Join Team B
async def join_B(update: Update, context: CallbackContext):
    await join_team(update, context, "B")

# ✅ Join Team Helper
async def join_team(update: Update, context: CallbackContext, team):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    teams = load_json(TEAMS_FILE)

    if str(chat_id) not in teams:
        await update.message.reply_text("⚠️ No active game. Referee use /create_team first.")
        return

    if is_user_in_any_team(chat_id, user_id):
        await update.message.reply_text("⚠️ You are already in a team!")
        return

    game = teams[str(chat_id)]
    team_key = "team_A" if team == "A" else "team_B"
    if len(game[team_key]["players"]) >= 8:
        await update.message.reply_text(f"⚠️ Team {team} is full (8 players max).")
        return

    game[team_key]["players"].append(user_id)
    save_json(TEAMS_FILE, teams)
    await update.message.reply_text(f"✅ {update.effective_user.first_name} joined Team {team}!")

# ✅ Set Captain
async def set_captain(update: Update, context: CallbackContext):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /captain <A/B> <player_id>")
        return

    chat_id = update.effective_chat.id
    teams = load_json(TEAMS_FILE)
    if str(chat_id) not in teams:
        await update.message.reply_text("⚠️ No active game!")
        return

    game = teams[str(chat_id)]
    if update.effective_user.id != game["referee"]:
        await update.message.reply_text("⚠️ Only referee can set captain!")
        return

    team = context.args[0].upper()
    player_id = int(context.args[1])
    team_key = "team_A" if team == "A" else "team_B"
    game[team_key]["captain"] = player_id
    save_json(TEAMS_FILE, teams)
    await update.message.reply_text(f"👑 Player {player_id} is now Captain of Team {team}")

# ✅ Set Goalkeeper
async def set_gk(update: Update, context: CallbackContext):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /gk <A/B> <player_id>")
        return

    chat_id = update.effective_chat.id
    teams = load_json(TEAMS_FILE)
    if str(chat_id) not in teams:
        await update.message.reply_text("⚠️ No active game!")
        return

    game = teams[str(chat_id)]
    if update.effective_user.id != game["referee"]:
        await update.message.reply_text("⚠️ Only referee can set goalkeeper!")
        return

    team = context.args[0].upper()
    player_id = int(context.args[1])
    team_key = "team_A" if team == "A" else "team_B"
    game[team_key]["gk"] = player_id
    save_json(TEAMS_FILE, teams)
    await update.message.reply_text(f"🧤 Player {player_id} is now Goalkeeper of Team {team}")

# ✅ Change Goalkeeper
async def change_gk(update: Update, context: CallbackContext):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /change_GK <A/B> <player_id>")
        return

    chat_id = update.effective_chat.id
    teams = load_json(TEAMS_FILE)
    if str(chat_id) not in teams:
        await update.message.reply_text("⚠️ No active game!")
        return

    game = teams[str(chat_id)]
    if update.effective_user.id != game["referee"]:
        await update.message.reply_text("⚠️ Only referee can change goalkeeper!")
        return

    team = context.args[0].upper()
    player_id = int(context.args[1])
    team_key = "team_A" if team == "A" else "team_B"
    old_gk = game[team_key]["gk"]
    game[team_key]["gk"] = player_id
    save_json(TEAMS_FILE, teams)
    await update.message.reply_text(f"🔄 Goalkeeper changed in Team {team}: {old_gk} → {player_id}")

# ✅ Register Handlers
def register_handlers(app):
    app.add_handler(CommandHandler("create_team", create_team))
    app.add_handler(CommandHandler("join_A", join_A))
    app.add_handler(CommandHandler("join_B", join_B))
    app.add_handler(CommandHandler("captain", set_captain))
    app.add_handler(CommandHandler("gk", set_gk))
    app.add_handler(CommandHandler("change_GK", change_gk))
