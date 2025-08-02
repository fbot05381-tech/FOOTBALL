from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, CallbackContext

# ✅ /start command
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("✅ Bot is Active!\nUse /start_football to begin.")

# ✅ /start_football command
async def start_football(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("🏆 Tournament Mode", callback_data="tournament_mode")],
        [InlineKeyboardButton("👥 Team Mode", callback_data="team_mode")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("⚽ Choose Game Mode:", reply_markup=reply_markup)

# ✅ Callback query handler
async def mode_selection(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    if query.data == "tournament_mode":
        await query.message.reply_text("🏆 Tournament Mode selected!\nUse /create_tournament to start.")
    elif query.data == "team_mode":
        await query.message.reply_text("👥 Team Mode selected!\nReferee use /create_team to start team setup.")

# ✅ Register Handlers
def register_handlers(app):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("start_football", start_football))
    app.add_handler(CallbackQueryHandler(mode_selection))
