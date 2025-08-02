import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, Chat
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# ✅ Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = "7496362823:AAHpnck9YF3HmaPU7lYIOqKMD1TfpHirUmE"

# ✅ Utility to check group
async def is_group(update: Update):
    return update.effective_chat.type in [Chat.GROUP, Chat.SUPERGROUP]

# ✅ Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_group(update):
        return  # DM में कुछ नहीं करेगा
    await update.message.reply_text("✅ Football Bot Active in this group! Use /start_football")

# ✅ Start Football
async def start_football(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_group(update):
        return
    keyboard = [
        [InlineKeyboardButton("🏆 Tournament Mode", callback_data="tournament_mode")],
        [InlineKeyboardButton("👥 Team Mode", callback_data="team_mode")],
    ]
    await update.message.reply_text("⚽ Choose Game Mode:", reply_markup=InlineKeyboardMarkup(keyboard))

# ✅ Button Handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.message.chat.type not in [Chat.GROUP, Chat.SUPERGROUP]:
        await query.answer()  # DM में ignore
        return
    await query.answer()
    if query.data == "tournament_mode":
        await query.message.reply_text("🏆 Tournament Mode selected!\nUse /create_tournament to start.")
    elif query.data == "team_mode":
        await query.message.reply_text("👥 Team Mode selected!\nReferee use /create_team to start team setup.")

# ✅ Tournament Commands (Only Groups)
async def create_tournament(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_group(update):
        return
    await update.message.reply_text("🏆 Tournament Created!\nNow use /total_team <number>")

async def total_team(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_group(update):
        return
    await update.message.reply_text("✅ Total Teams set!\nUse /team_members <min>-<max>")

async def team_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_group(update):
        return
    await update.message.reply_text("✅ Team size set! Registration started.")

# ✅ Main
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("start_football", start_football))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(CommandHandler("create_tournament", create_tournament))
    app.add_handler(CommandHandler("total_team", total_team))
    app.add_handler(CommandHandler("team_members", team_members))

    print("✅ Bot Running (Only Groups)...")
    app.run_polling(allowed_updates=["message", "chat_member", "callback_query"])
