import os
import logging
from telegram.ext import ApplicationBuilder
from handlers import start, team_mode, tournament_mode, referee, gameplay

# ✅ Logging for debugging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# ✅ Bot Token from environment
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN not set! Please set environment variable before running.")

# ✅ Create Telegram Application
app = ApplicationBuilder().token(BOT_TOKEN).build()

# ✅ Register all command & callback handlers
start.register_handlers(app)
team_mode.register_handlers(app)
tournament_mode.register_handlers(app)
referee.register_handlers(app)
gameplay.register_handlers(app)

# ✅ Main entry point
if __name__ == "__main__":
    logger.info("✅ Football Game Bot is running...")
    app.run_polling()
