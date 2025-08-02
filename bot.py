import os
from telegram.ext import Application
from handlers.start import register_handlers as start_handlers
from handlers.team_mode import register_handlers as team_handlers
from handlers.tournament_mode import register_handlers as tournament_handlers
from handlers.referee import register_handlers as referee_handlers
from handlers.gameplay import register_handlers as gameplay_handlers

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    print("❌ BOT_TOKEN missing! Set environment variable.")
    exit()

async def main():
    app = Application.builder().token(BOT_TOKEN).build()
    start_handlers(app)
    team_handlers(app)
    tournament_handlers(app)
    referee_handlers(app)
    gameplay_handlers(app)
    print("✅ Football Bot Running...")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
