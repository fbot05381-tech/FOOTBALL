import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from flask import Flask, request
import telegram
import os

# ✅ Config
TOKEN = "7496362823:AAHpnck9YF3HmaPU7lYIOqKMD1TfpHirUmE"
PORT = int(os.environ.get("PORT", 5000))
WEBHOOK_URL = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/webhook"

# ✅ Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Telegram Bot API
bot_app = ApplicationBuilder().token(TOKEN).build()

# ✅ Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot is Active! Use /start_football")

async def start_football(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🏆 Tournament Mode", callback_data="tournament_mode")],
        [InlineKeyboardButton("👥 Team Mode", callback_data="team_mode")],
    ]
    await update.message.reply_text("⚽ Choose Game Mode:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    logger.info(f"Callback Query: {query.data}")

    if query.data == "tournament_mode":
        await query.message.reply_text("🏆 Tournament Mode selected!")
    elif query.data == "team_mode":
        await query.message.reply_text("👥 Team Mode selected!")

bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CommandHandler("start_football", start_football))
bot_app.add_handler(CallbackQueryHandler(button_handler))

# ✅ Flask Webhook Server
flask_app = Flask(__name__)
tg_bot = telegram.Bot(token=TOKEN)

@flask_app.route("/webhook", methods=["POST"])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), tg_bot)
    bot_app.update_queue.put_nowait(update)
    return "OK"

@flask_app.route("/")
def home():
    return "Football Bot Running!"

if __name__ == "__main__":
    import asyncio
    async def set_webhook():
        await tg_bot.set_webhook(url=WEBHOOK_URL)
        logger.info(f"✅ Webhook set: {WEBHOOK_URL}")

    asyncio.get_event_loop().run_until_complete(set_webhook())
    flask_app.run(host="0.0.0.0", port=PORT)
