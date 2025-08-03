import os
import json

# ✅ Paths for JSON database files
DB_FOLDER = "database"
MATCH_DB = os.path.join(DB_FOLDER, "match_data.json")
PLAYER_DB = os.path.join(DB_FOLDER, "player_data.json")
TOURNAMENT_DB = os.path.join(DB_FOLDER, "tournament_data.json")

# ✅ Ensure database folder exists
os.makedirs(DB_FOLDER, exist_ok=True)

# ✅ Initialize DB files if missing
def init_db():
    for file in [MATCH_DB, PLAYER_DB, TOURNAMENT_DB]:
        if not os.path.exists(file):
            with open(file, "w") as f:
                json.dump({}, f)

# ✅ Read JSON
def read_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)

# ✅ Write JSON
def write_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)
