import os
import logging
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot Active! Use /start_football")

async def start_football(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🏆 Tournament Mode", callback_data="tournament_mode")],
        [InlineKeyboardButton("👥 Team Mode", callback_data="team_mode")]
    ]
    await update.message.reply_text("⚽ Choose Game Mode:", reply_markup=InlineKeyboardMarkup(keyboard))

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    logger.info(f"Callback Query Received: {data}")

    if data == "tournament_mode":
        await query.message.reply_text("🏆 Tournament Mode selected!")
    elif data == "team_mode":
        await query.message.reply_text("👥 Team Mode selected!")

if __name__ == "__main__":
    if not TOKEN:
        raise ValueError("BOT_TOKEN not set!")

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("start_football", start_football))
    app.add_handler(CallbackQueryHandler(callback_handler))
    logger.info("✅ Bot running...")
    app.run_polling()
