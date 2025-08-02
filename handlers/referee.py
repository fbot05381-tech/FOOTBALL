from telegram import Update
from telegram.ext import CommandHandler, CallbackContext
from config import TEAMS_FILE
from handlers.utils import load_json, save_json

# ✅ Replace Player Command
async def replace_player(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    teams = load_json(TEAMS_FILE)

    if str(chat_id) not in teams:
        await update.message.reply_text("⚠️ No game running!")
        return

    game = teams[str(chat_id)]
    referee = game.get("referee")

    if update.effective_user.id != referee:
        await update.message.reply_text("⚠️ Only the referee can replace players!")
        return

    if len(context.args) < 3:
        await update.message.reply_text("Usage: /replace <A/B> <old_player_id> <new_player_id>")
        return

    team_name = context.args[0].upper()
    old_id = int(context.args[1])
    new_id = int(context.args[2])
    team_key = "team_A" if team_name == "A" else "team_B"

    try:
        players = game[team_key]["players"]
        players.remove(old_id)
        players.append(new_id)
        save_json(TEAMS_FILE, teams)
        await update.message.reply_text(
            f"🔄 Player {old_id} replaced with {new_id} in Team {team_name}."
        )
    except:
        await update.message.reply_text("⚠️ Error replacing player!")

# ✅ Change Referee Command
async def change_referee(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    teams = load_json(TEAMS_FILE)

    if str(chat_id) not in teams:
        await update.message.reply_text("⚠️ No game running!")
        return

    game = teams[str(chat_id)]
    referee = game.get("referee")

    if len(context.args) < 1:
        await update.message.reply_text("Usage: /change_referee <new_referee_id>")
        return

    new_ref = int(context.args[0])

    if update.effective_user.id != referee:
        await update.message.reply_text("⚠️ Only the current referee can change referee!")
        return

    game["referee"] = new_ref
    save_json(TEAMS_FILE, teams)
    await update.message.reply_text(f"👨‍⚖️ Referee changed to {new_ref}")

# ✅ Register Handlers
def register_handlers(app):
    app.add_handler(CommandHandler("replace", replace_player))
    app.add_handler(CommandHandler("change_referee", change_referee))
