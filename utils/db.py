import json, os, asyncio, logging

DATA_DIR = "data"
MATCH_DB = os.path.join(DATA_DIR, "match.json")
PLAYER_DB = os.path.join(DATA_DIR, "players.json")
TOURNAMENT_DB = os.path.join(DATA_DIR, "tournament.json")

def ensure_data_files():
    os.makedirs(DATA_DIR, exist_ok=True)
    for file in [MATCH_DB, PLAYER_DB, TOURNAMENT_DB]:
        if not os.path.exists(file):
            with open(file, "w") as f:
                json.dump({}, f)

def read_json(path):
    with open(path, "r") as f:
        return json.load(f)

def write_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

async def init_db():
    ensure_data_files()
    logging.info("✅ Database initialized.")
    await asyncio.sleep(0)
