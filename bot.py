import logging
import os
from flask import Flask, request
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
import telegram
import asyncio

# ✅ Config
TOKEN = "7496362823:AAHpnck9YF3HmaPU7lYIOqKMD1TfpHirUmE"
PORT = int(os.environ.get("PORT", 5000))
WEBHOOK_URL = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/webhook"

# ✅ Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Telegram Bot + Flask
bot_app = ApplicationBuilder().token(TOKEN).build()
flask_app = Flask(__name__)
tg_bot = telegram.Bot(token=TOKEN)

# ✅ Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot Active! Use /start_football")

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
        await query.message.reply_text("🏆 Tournament Mode selected!\nUse /create_tournament to start.")
    elif query.data == "team_mode":
        await query.message.reply_text("👥 Team Mode selected!\nReferee use /create_team to start team setup.")

# ✅ Tournament commands
async def create_tournament(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("/create_tournament command triggered")
    await update.message.reply_text("🏆 Tournament Created!\nNow use /total_team <number>")

async def total_team(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Total Teams set!\nUse /team_members <min>-<max>")

async def team_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Team size set! Registration started.")

# ✅ Register Handlers
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CommandHandler("start_football", start_football))
bot_app.add_handler(CallbackQueryHandler(button_handler))
bot_app.add_handler(CommandHandler("create_tournament", create_tournament))
bot_app.add_handler(CommandHandler("total_team", total_team))
bot_app.add_handler(CommandHandler("team_members", team_members))

# ✅ Flask Webhook
@flask_app.route("/webhook", methods=["POST"])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), tg_bot)
    bot_app.update_queue.put_nowait(update)
    return "OK"

@flask_app.route("/")
def home():
    return "Football Bot Running!"

if __name__ == "__main__":
    async def set_webhook():
        await tg_bot.set_webhook(url=WEBHOOK_URL)
        logger.info(f"✅ Webhook set: {WEBHOOK_URL}")

    asyncio.get_event_loop().run_until_complete(set_webhook())
    flask_app.run(host="0.0.0.0", port=PORT)
