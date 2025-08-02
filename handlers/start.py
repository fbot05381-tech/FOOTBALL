from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, CallbackContext
from config import TEAMS_FILE
from handlers.utils import load_json, save_json

async def start_football(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("⚽ Team Mode", callback_data="mode_team")],
        [InlineKeyboardButton("🏆 Tournament Mode", callback_data="mode_tournament")]
    ]
    await update.message.reply_text("Choose Football Mode:", reply_markup=InlineKeyboardMarkup(keyboard))

async def mode_selection(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    if query.data == "mode_team":
        kb = [[InlineKeyboardButton("I'm the Referee", callback_data="be_referee")]]
        await query.message.reply_text("Team Mode Selected!\nReferee click below:", reply_markup=InlineKeyboardMarkup(kb))
    elif query.data == "mode_tournament":
        from handlers.tournament_mode import start_tournament_mode
        await start_tournament_mode(update, context)

async def be_referee(update: Update, context: CallbackContext):
    query = update.callback_query
    chat_id = query.message.chat_id
    teams = load_json(TEAMS_FILE)
    teams[str(chat_id)] = {
        "referee": query.from_user.id,
        "team_A": {"players": [], "captain": None, "gk": None},
        "team_B": {"players": [], "captain": None, "gk": None},
        "ball": None
    }
    save_json(TEAMS_FILE, teams)
    await query.message.reply_text(f"👨‍⚖️ {query.from_user.first_name} is the referee!\nUse /create_team")

def register_handlers(app):
    app.add_handler(CommandHandler("start_football", start_football))
    app.add_handler(CallbackQueryHandler(mode_selection, pattern="^mode_"))
    app.add_handler(CallbackQueryHandler(be_referee, pattern="^be_referee$"))
