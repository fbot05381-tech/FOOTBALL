import json
import os
from config import PLAYERS_FILE, TEAMS_FILE, TOURNAMENTS_FILE

# ✅ Load JSON
def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        try:
            return json.load(f)
        except:
            return {}

# ✅ Save JSON
def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

# ✅ Check if user is in any team in current chat
def is_user_in_any_team(chat_id, user_id):
    teams = load_json(TEAMS_FILE)
    chat_id = str(chat_id)
    if chat_id not in teams:
        return False

    game = teams[chat_id]
    if user_id in game["team_A"]["players"]:
        return True
    if user_id in game["team_B"]["players"]:
        return True
    return False

# ✅ 🔥 Global check: Is user in any group game?
def is_user_in_any_group(user_id):
    teams = load_json(TEAMS_FILE)
    for chat_id, game in teams.items():
        if user_id in game["team_A"]["players"] or user_id in game["team_B"]["players"]:
            return True
    return False

# ✅ Get user's team (A/B)
def get_user_team(chat_id, user_id):
    teams = load_json(TEAMS_FILE)
    chat_id = str(chat_id)
    if chat_id not in teams:
        return None
    game = teams[chat_id]
    if user_id in game["team_A"]["players"]:
        return "A"
    if user_id in game["team_B"]["players"]:
        return "B"
    return None

# ✅ Update Player Stats
def update_player_stat(user_id, stat_type):
    players = load_json(PLAYERS_FILE)
    user_id = str(user_id)
    if user_id not in players:
        players[user_id] = {"goals": 0, "steals": 0, "passes": 0}

    players[user_id][stat_type] += 1
    save_json(PLAYERS_FILE, players)

# ✅ Get MVP
def get_mvp():
    players = load_json(PLAYERS_FILE)
    if not players:
        return None
    mvp = max(players.items(), key=lambda x: x[1]["goals"] + x[1]["steals"] + x[1]["passes"])
    return mvp[0]
