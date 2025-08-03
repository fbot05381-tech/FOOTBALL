import json, os

DB_FILE = "database.json"

def init_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump({"matches": {}, "players": {}}, f)

def load_db():
    init_db()
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

# --- Player Stats ---
def add_goal(player):
    db = load_db()
    if player not in db["players"]:
        db["players"][player] = {"goals": 0, "assists": 0, "matches": 0}
    db["players"][player]["goals"] += 1
    save_db(db)

def add_assist(player):
    db = load_db()
    if player not in db["players"]:
        db["players"][player] = {"goals": 0, "assists": 0, "matches": 0}
    db["players"][player]["assists"] += 1
    save_db(db)

def add_match(player):
    db = load_db()
    if player not in db["players"]:
        db["players"][player] = {"goals": 0, "assists": 0, "matches": 0}
    db["players"][player]["matches"] += 1
    save_db(db)

def get_player_stats(player):
    db = load_db()
    return db["players"].get(player, {"goals": 0, "assists": 0, "matches": 0})
