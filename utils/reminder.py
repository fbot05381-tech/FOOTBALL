import asyncio
import logging
from aiogram import Bot
from utils.db import read_json, MATCH_DB

logger = logging.getLogger(__name__)

async def reminder_loop(bot: Bot):
    logger.info("🔄 Reminder loop started...")
    while True:
        try:
            await asyncio.sleep(900)  # ✅ हर 15 मिनट पर check

            match_data = read_json(MATCH_DB)
            if match_data.get("paused"):
                chat_id = match_data.get("chat_id")
                if chat_id:
                    await bot.send_message(chat_id, "⏸️ Match अभी PAUSED है! Referee resume करे।")
            else:
                chat_id = match_data.get("chat_id")
                if chat_id:
                    await bot.send_message(chat_id, "⚽ Friendly Reminder: Match चल रहा है, moves करो!")

        except Exception as e:
            logger.error(f"⚠️ Reminder loop error: {e}")
            await asyncio.sleep(10)
