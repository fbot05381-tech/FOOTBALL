import random
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext
from config import TOURNAMENTS_FILE
from handlers.utils import load_json, save_json

# ✅ Create Tournament (Owner)
async def create_tournament(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    tournaments = load_json(TOURNAMENTS_FILE)

    tournaments[str(chat_id)] = {
        "owner": update.effective_user.id,
        "total_teams": None,
        "team_members": {"min": 4, "max": 10},
        "teams": {},
        "schedule": [],
        "points": {}
    }
    save_json(TOURNAMENTS_FILE, tournaments)
    await update.message.reply_text("🏆 Tournament Created!\nUse /total_team <4-10> to set number of teams.")

# ✅ Set Total Teams
async def total_team(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    tournaments = load_json(TOURNAMENTS_FILE)

    if str(chat_id) not in tournaments:
        await update.message.reply_text("⚠️ No active tournament. Use /create_tournament first.")
        return

    if update.effective_user.id != tournaments[str(chat_id)]["owner"]:
        await update.message.reply_text("⚠️ Only the owner can set total teams.")
        return

    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Usage: /total_team <4-10>")
        return

    num = int(context.args[0])
    if num < 4 or num > 10:
        await update.message.reply_text("⚠️ Total teams must be between 4 and 10.")
        return

    tournaments[str(chat_id)]["total_teams"] = num
    save_json(TOURNAMENTS_FILE, tournaments)
    await update.message.reply_text(f"✅ Total teams set to {num}.\nUse /team_members <min-max> to set players per team.")

# ✅ Set Team Members Min-Max
async def team_members(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    tournaments = load_json(TOURNAMENTS_FILE)

    if str(chat_id) not in tournaments:
        await update.message.reply_text("⚠️ No active tournament.")
        return

    if update.effective_user.id != tournaments[str(chat_id)]["owner"]:
        await update.message.reply_text("⚠️ Only owner can set team members.")
        return

    if len(context.args) < 1 or "-" not in context.args[0]:
        await update.message.reply_text("Usage: /team_members <min-max>")
        return

    try:
        min_p, max_p = map(int, context.args[0].split("-"))
    except:
        await update.message.reply_text("⚠️ Invalid format. Use /team_members 4-8")
        return

    if min_p < 4 or max_p > 10 or min_p > max_p:
        await update.message.reply_text("⚠️ Min 4 and Max 10 players allowed.")
        return

    tournaments[str(chat_id)]["team_members"] = {"min": min_p, "max": max_p}
    save_json(TOURNAMENTS_FILE, tournaments)
    await update.message.reply_text(f"✅ Team members per team set: {min_p}-{max_p}")

# ✅ Register Teams
async def register_team(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    tournaments = load_json(TOURNAMENTS_FILE)

    if str(chat_id) not in tournaments:
        await update.message.reply_text("⚠️ No active tournament.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("Usage: /register_team <TeamName> <CaptainUsername>")
        return

    team_name = context.args[0]
    captain = context.args[1]
    tournament = tournaments[str(chat_id)]

    if team_name in tournament["teams"]:
        await update.message.reply_text("⚠️ Team already registered.")
        return

    if len(tournament["teams"]) >= tournament["total_teams"]:
        await update.message.reply_text("⚠️ All teams are already registered.")
        return

    tournament["teams"][team_name] = {"captain": captain, "points": 0}
    tournament["points"][team_name] = 0
    save_json(TOURNAMENTS_FILE, tournaments)

    await update.message.reply_text(f"✅ Team {team_name} registered with Captain @{captain}")

# ✅ Generate Match Schedule
async def generate_schedule(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    tournaments = load_json(TOURNAMENTS_FILE)

    if str(chat_id) not in tournaments:
        await update.message.reply_text("⚠️ No active tournament.")
        return

    tournament = tournaments[str(chat_id)]
    teams = list(tournament["teams"].keys())
    if len(teams) < 2:
        await update.message.reply_text("⚠️ At least 2 teams required.")
        return

    schedule = []
    for i in range(len(teams)):
        for j in range(i+1, len(teams)):
            schedule.append((teams[i], teams[j]))

    random.shuffle(schedule)
    tournament["schedule"] = schedule
    save_json(TOURNAMENTS_FILE, tournaments)

    msg = "📅 Tournament Schedule:\n"
    for match in schedule:
        msg += f"{match[0]} vs {match[1]}\n"
    await update.message.reply_text(msg)

# ✅ Points Table
async def points_table(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    tournaments = load_json(TOURNAMENTS_FILE)

    if str(chat_id) not in tournaments:
        await update.message.reply_text("⚠️ No active tournament.")
        return

    points = tournaments[str(chat_id)]["points"]
    msg = "🏆 Points Table:\n"
    sorted_points = sorted(points.items(), key=lambda x: x[1], reverse=True)
    for team, pts in sorted_points:
        msg += f"{team}: {pts} pts\n"

    await update.message.reply_text(msg)

# ✅ Start Tournament Mode (from start.py)
async def start_tournament_mode(update: Update, context: CallbackContext):
    await update.callback_query.message.reply_text(
        "🏆 Tournament Mode Selected!\nOwner use /create_tournament to begin.")

# ✅ Register Handlers
def register_handlers(app):
    app.add_handler(CommandHandler("create_tournament", create_tournament))
    app.add_handler(CommandHandler("total_team", total_team))
    app.add_handler(CommandHandler("team_members", team_members))
    app.add_handler(CommandHandler("register_team", register_team))
    app.add_handler(CommandHandler("generate_schedule", generate_schedule))
    app.add_handler(CommandHandler("points_table", points_table))
