import time
import math

# ✅ Cooldown System
cooldowns = {}

def cooldown_check(chat_id, command, gap):
    now = time.time()
    key = f"{chat_id}:{command}"
    if key in cooldowns and now - cooldowns[key] < gap:
        return False
    return True

def set_cooldown(chat_id, command):
    key = f"{chat_id}:{command}"
    cooldowns[key] = time.time()

# ✅ Time Formatter
def format_time(seconds):
    seconds = int(seconds)
    minutes = seconds // 60
    sec = seconds % 60
    return f"{minutes:02d}:{sec:02d}"
