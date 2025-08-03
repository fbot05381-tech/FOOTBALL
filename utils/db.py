import json
import os

# ✅ Database file paths
DB_FOLDER = "database"
MATCH_DB = os.path.join(DB_FOLDER, "match_data.json")
PLAYER_DB = os.path.join(DB_FOLDER, "player_data.json")
TOURNAMENT_DB = os.path.join(DB_FOLDER, "tournament_data.json")

# ✅ Ensure DB folder exists
def ensure_db():
    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER)
    for file in [MATCH_DB, PLAYER_DB, TOURNAMENT_DB]:
        if not os.path.exists(file):
            with open(file, "w") as f:
                json.dump({}, f)

# ✅ Initialize DB (called on startup)
def init_db():
    ensure_db()
    print("📂 Database initialized.")

# ✅ Read JSON safely
async def read_json(file_path):
    ensure_db()
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

# ✅ Write JSON safely
async def write_json(file_path, data):
    ensure_db()
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)
