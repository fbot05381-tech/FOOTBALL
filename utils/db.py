import json, os

DB_FILE = "database/match_data.json"

# ✅ Ensure folder exists
os.makedirs("database", exist_ok=True)

# ✅ Default data structure
default_data = {
    "teams": {"A": [], "B": []},
    "score": {"A": {}, "B": {}},
    "last_pass": None,
    "current_round": 0,
    "time_left": 0,
    "status": "idle",
    "paused": False
}

# ✅ Load Data
def get_match_data():
    if not os.path.exists(DB_FILE):
        save_match_data(default_data)
    with open(DB_FILE, "r") as f:
        return json.load(f)

# ✅ Save Data
def save_match_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ✅ Reset
def reset_match_data():
    save_match_data(default_data)

# ✅ Add Goal
def add_goal(team, player):
    data = get_match_data()
    if player not in data["score"][team]:
        data["score"][team][player] = {"goals": 0, "assists": 0}
    data["score"][team][player]["goals"] += 1
    if data["last_pass"] and data["last_pass"] != player:
        add_assist(data["last_pass"])
    save_match_data(data)

# ✅ Add Assist
def add_assist(player):
    data = get_match_data()
    for team in ["A", "B"]:
        if player in data["score"][team]:
            data["score"][team][player]["assists"] += 1
            break
    save_match_data(data)

# ✅ Set Last Pass
def set_last_pass(player):
    data = get_match_data()
    data["last_pass"] = player
    save_match_data(data)

# ✅ Pause / Resume
def pause_match():
    data = get_match_data()
    data["paused"] = True
    save_match_data(data)

def resume_match():
    data = get_match_data()
    data["paused"] = False
    save_match_data(data)

def is_paused():
    data = get_match_data()
    return data.get("paused", False)

# ✅ Scoreboard Text
def get_scoreboard_text(data):
    text = "🏆 <b>Football Match Scoreboard</b>\n\n"
    for team in ["A", "B"]:
        text += f"<b>Team {team}</b>\n"
        for idx, player in enumerate(data["teams"][team], start=1):
            stats = data["score"][team].get(player, {"goals": 0, "assists": 0})
            text += f"{idx}️⃣ {player} | Goals: {stats['goals']} | Assists: {stats['assists']}\n"
        text += "\n"
    # MVP Calculation
    mvp = None
    max_score = -1
    for team in ["A", "B"]:
        for player, stats in data["score"][team].items():
            score_value = stats["goals"] * 2 + stats["assists"]
            if score_value > max_score:
                max_score = score_value
                mvp = player
    if mvp:
        text += f"🔥 <b>Current MVP:</b> {mvp}\n"
    return f"<pre>{text}</pre>"
