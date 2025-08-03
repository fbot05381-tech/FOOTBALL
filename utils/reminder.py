import asyncio
import logging
from aiogram import Bot

REMINDER_INTERVAL = 900  # 15 minutes (900 sec)

reminder_task = None
match_active = False
match_paused = False
chat_id_global = None

async def reminder_loop(bot: Bot, chat_id: int, get_scoreboard):
    global match_active, chat_id_global
    chat_id_global = chat_id
    match_active = True
    logging.info("✅ Reminder loop started...")

    while match_active:
        await asyncio.sleep(REMINDER_INTERVAL)
        if match_active and not match_paused:
            try:
                scoreboard_text, gif_id = get_scoreboard()
                await bot.send_animation(chat_id, animation=gif_id, caption=f"⏰ 15 min update:\n\n{scoreboard_text}")
            except Exception as e:
                logging.error(f"⚠️ Reminder send failed: {e}")

def stop_reminder():
    global match_active
    match_active = False
    logging.info("🛑 Reminder loop stopped.")

def pause_reminder():
    global match_paused
    match_paused = True
    logging.info("⏸️ Reminder paused.")

def resume_reminder():
    global match_paused
    match_paused = False
    logging.info("▶️ Reminder resumed.")
