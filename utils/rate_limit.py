import time

# {user_id: {command: last_used_timestamp}}
COOLDOWN_TRACKER = {}

# Default cooldown times (seconds)
COOLDOWNS = {
    "score": 30,
    "start": 10,
    "add": 10,
    "remove": 10,
    "pause": 10,
    "resume": 10
}

async def check_cooldown(user_id, command, bot, chat_id):
    now = time.time()
    user_cd = COOLDOWN_TRACKER.get(user_id, {})

    cd_time = COOLDOWNS.get(command, 10)

    if command in user_cd and now - user_cd[command] < cd_time:
        remain = int(cd_time - (now - user_cd[command]))
        await bot.send_message(chat_id, f"⏳ Wait {remain}s before using /{command} again.")
        return False

    user_cd[command] = now
    COOLDOWN_TRACKER[user_id] = user_cd
    return True
