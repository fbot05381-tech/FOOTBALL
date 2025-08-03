import json
import os
import asyncio
import logging

logger = logging.getLogger(__name__)

# ✅ JSON file paths
DATA_DIR = "data"
MATCH_DB = os.path.join(DATA_DIR, "match.json")
PLAYER_DB = os.path.join(DATA_DIR, "players.json")
TOURNAMENT_DB = os.path.join(DATA_DIR, "tournament.json")

# ✅ Safe read
def read_json(path):
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"❌ Error reading {path}: {e}")
        return {}

# ✅ Safe write
def write_json(path, data):
    os.makedirs(DATA_DIR, exist_ok=True)
    try:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"❌ Error writing {path}: {e}")

# ✅ Async init
async def init_db():
    os.makedirs(DATA_DIR, exist_ok=True)

    # Create default files if not exist
    for path in [MATCH_DB, PLAYER_DB, TOURNAMENT_DB]:
        if not os.path.exists(path):
            write_json(path, {})

    await asyncio.sleep(0)  # Make it awaitable
    logger.info("✅ Database initialized.")
