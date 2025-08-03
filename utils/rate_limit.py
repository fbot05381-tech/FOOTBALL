import time
from aiogram import Bot

last_command_time = {}
score_last_used = {}

GLOBAL_COOLDOWN = 10
SCORE_COOLDOWN = 30

COOLDOWN_GIF = "CgACAgQAAxkBAANHZCoolDownGIFID"  # अपनी gif का file_id डालना

async def check_cooldown(user_id, command, bot: Bot, chat_id):
    now = time.time()

    # Global 10s gap
    if user_id in last_command_time and now - last_command_time[user_id] < GLOBAL_COOLDOWN:
        wait_time = int(GLOBAL_COOLDOWN - (now - last_command_time[user_id]))
        await bot.send_animation(chat_id, animation=COOLDOWN_GIF, caption=f"⏳ Wait {wait_time}s before next command!")
        return False
    last_command_time[user_id] = now

    # /score 30s gap
    if command == "score":
        if user_id in score_last_used and now - score_last_used[user_id] < SCORE_COOLDOWN:
            wait_time = int(SCORE_COOLDOWN - (now - score_last_used[user_id]))
            await bot.send_animation(chat_id, animation=COOLDOWN_GIF, caption=f"📊 /score cooldown active! Wait {wait_time}s")
            return False
        score_last_used[user_id] = now

    return True
