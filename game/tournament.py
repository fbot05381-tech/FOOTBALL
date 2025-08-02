from telegram import Update
from telegram.ext import ContextTypes
from utils.database import db

async def register_team(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user

    print(f"📌 register_team called in chat {chat_id} by {user.id}")

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
    print(f"📌 Trying to register team: {team_name}")

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

async def join_team(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user

    print(f"📌 join_team called in chat {chat_id} by {user.id}")

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
    print(f"📌 Trying to join team: {team_name}")

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
