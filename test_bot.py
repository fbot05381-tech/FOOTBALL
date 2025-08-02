from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram import Update

TOKEN = "7496362823:AAHpnck9YF3HmaPU7lYIOqKMD1TfpHirUmE"

async def register_team(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"✅ Register Command Triggered! Args: {context.args}")

async def join_team(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"✅ Join Command Triggered! Args: {context.args}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("register_team", register_team))
    app.add_handler(CommandHandler("join_team", join_team))
    print("✅ Minimal Bot Running...")
    app.run_polling()
