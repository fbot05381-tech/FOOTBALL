import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Chat
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# ✅ Imports from game
from game.team_mode import handle_team_mode, create_team
from game.tournament import (
    handle_tournament_mode,
    create_tournament,
    total_team,
    team_members,
    register_team,
    join_team
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = "YOUR_BOT_TOKEN"

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

# ✅ Button Handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.message.chat.type not in [Chat.GROUP, Chat.SUPERGROUP]:
        await query.answer(); return
    await query.answer()

    if query.data == "tournament_mode":
        await handle_tournament_mode(query)
    elif query.data == "team_mode":
        await handle_team_mode(query)

# ✅ Main
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    # 🔹 Start commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("start_football", start_football))
    app.add_handler(CallbackQueryHandler(button_handler))

    # 🔹 Tournament commands (सही क्रम में)
    app.add_handler(CommandHandler("create_tournament", create_tournament))
    app.add_handler(CommandHandler("total_team", total_team))
    app.add_handler(CommandHandler("team_members", team_members))
    app.add_handler(CommandHandler("register_team", register_team))  # ✅ Added
    app.add_handler(CommandHandler("join_team", join_team))          # ✅ Added

    # 🔹 Team mode commands
    app.add_handler(CommandHandler("create_team", create_team))

    print("✅ Football Bot Running...")
    app.run_polling(allowed_updates=["message", "chat_member", "callback_query"])
