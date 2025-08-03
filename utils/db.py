import json
import os
import asyncio

DB_DIR = "database"
PLAYER_DB = os.path.join(DB_DIR, "players.json")
MATCH_DB = os.path.join(DB_DIR, "match.json")
TOURNAMENT_DB = os.path.join(DB_DIR, "tournament.json")

# ✅ Ensure DB folder exists
os.makedirs(DB_DIR, exist_ok=True)

# ✅ Safe read/write
def read_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# ✅ Async-safe init_db
async def init_db():
    loop = asyncio.get_event_loop()
    def _init():
        if not os.path.exists(PLAYER_DB):
            write_json(PLAYER_DB, {})
        if not os.path.exists(MATCH_DB):
            write_json(MATCH_DB, {})
        if not os.path.exists(TOURNAMENT_DB):
            write_json(TOURNAMENT_DB, {})
    await loop.run_in_executor(None, _init)
    return True
