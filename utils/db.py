import json
import os

DB_FOLDER = "database"
TEAM_DB = os.path.join(DB_FOLDER, "teams.json")
STATS_DB = os.path.join(DB_FOLDER, "stats.json")
TOURNAMENT_DB = os.path.join(DB_FOLDER, "tournament.json")

def ensure_folder():
    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER)

def init_file(path):
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump({}, f)

async def init_db():
    ensure_folder()
    init_file(TEAM_DB)
    init_file(STATS_DB)
    init_file(TOURNAMENT_DB)

def read_json(path):
    ensure_folder()
    with open(path, "r") as f:
        return json.load(f)

def write_json(path, data):
    ensure_folder()
    with open(path, "w") as f:
        json.dump(data, f, indent=4)
