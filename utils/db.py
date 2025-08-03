import json
import os

# ✅ Database file paths
DB_FOLDER = "database"
MATCH_DB = os.path.join(DB_FOLDER, "matches.json")
PLAYER_DB = os.path.join(DB_FOLDER, "players.json")

# ✅ Create folder & empty files if missing
def init_db():
    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER)
    for file in [MATCH_DB, PLAYER_DB]:
        if not os.path.exists(file):
            with open(file, "w") as f:
                json.dump({}, f)

# ✅ Read JSON file
def read_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

# ✅ Write JSON file
def write_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)
