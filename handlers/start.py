from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ Bot is Active!\nUse /start_football to begin."
    )

async def start_football(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚽ Choose Game Mode:\n"
        "Type /team_mode for Team Mode\n"
        "Type /tournament_mode for Tournament Mode"
    )

async def team_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👥 Team Mode selected!\nReferee use /create_team to start team setup."
    )

async def tournament_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏆 Tournament Mode selected!\nUse /create_tournament to start."
    )

def register_handlers(app):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("start_football", start_football))
    app.add_handler(CommandHandler("team_mode", team_mode))
    app.add_handler(CommandHandler("tournament_mode", tournament_mode))
