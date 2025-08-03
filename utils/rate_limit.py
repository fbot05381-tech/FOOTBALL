import time

last_command_time = {}
score_last_used = {}

GLOBAL_COOLDOWN = 10
SCORE_COOLDOWN = 30

def can_use_command(user_id, command):
    now = time.time()

    # Global 10 sec gap
    if user_id in last_command_time and now - last_command_time[user_id] < GLOBAL_COOLDOWN:
        return False, f"⏳ Please wait {int(GLOBAL_COOLDOWN - (now - last_command_time[user_id]))}s before using another command."
    last_command_time[user_id] = now

    # /score 30 sec gap
    if command == "score":
        if user_id in score_last_used and now - score_last_used[user_id] < SCORE_COOLDOWN:
            return False, f"⏳ /score can be used again after {int(SCORE_COOLDOWN - (now - score_last_used[user_id]))}s."
        score_last_used[user_id] = now

    return True, None
