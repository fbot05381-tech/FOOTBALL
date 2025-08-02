from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackContext

# ✅ Start Command
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("✅ Football Bot is Active!\nUse /start_football to begin.")

# ✅ Start Football Command
async def start_football(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("🏆 Tournament Mode", callback_data="tournament_mode")],
        [InlineKeyboardButton("👥 Team Mode", callback_data="team_mode")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("⚽ Choose Game Mode:", reply_markup=reply_markup)

# ✅ Register Handlers
def register_handlers(app):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("start_football", start_football))
