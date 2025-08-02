import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# ✅ Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = "7496362823:AAHpnck9YF3HmaPU7lYIOqKMD1TfpHirUmE"

# ✅ Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("DEBUG: /start triggered")
    await update.message.reply_text("✅ Bot Active! Use /start_football")

# ✅ Start Football Command
async def start_football(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("DEBUG: /start_football triggered")
    keyboard = [
        [InlineKeyboardButton("🏆 Tournament Mode", callback_data="tournament_mode")],
        [InlineKeyboardButton("👥 Team Mode", callback_data="team_mode")],
    ]
    await update.message.reply_text("⚽ Choose Game Mode:", reply_markup=InlineKeyboardMarkup(keyboard))

# ✅ Button Handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    logger.info(f"DEBUG: Button Clicked: {query.data}")

    if query.data == "tournament_mode":
        await query.message.reply_text("🏆 Tournament Mode selected!\nUse /create_tournament to start.")
    elif query.data == "team_mode":
        await query.message.reply_text("👥 Team Mode selected!\nReferee use /create_team to start team setup.")

# ✅ Tournament Commands
async def create_tournament(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("DEBUG: /create_tournament triggered")
    await update.message.reply_text("🏆 Tournament Created!\nNow use /total_team <number>")

async def total_team(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("DEBUG: /total_team triggered")
    await update.message.reply_text("✅ Total Teams set!\nUse /team_members <min>-<max>")

async def team_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("DEBUG: /team_members triggered")
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

    print("✅ Bot Running with Polling...")
    app.run_polling()
