import json
import os
import aiofiles

DATA_DIR = "data"
PLAYER_DB = os.path.join(DATA_DIR, "players.json")
MATCH_DB = os.path.join(DATA_DIR, "matches.json")
TOURNAMENT_DB = os.path.join(DATA_DIR, "tournaments.json")

async def init_db():
    os.makedirs(DATA_DIR, exist_ok=True)
    for file in [PLAYER_DB, MATCH_DB, TOURNAMENT_DB]:
        if not os.path.exists(file):
            async with aiofiles.open(file, "w") as f:
                await f.write("{}")

async def read_json(path):
    async with aiofiles.open(path, "r") as f:
        data = await f.read()
        return json.loads(data)

async def write_json(path, data):
    async with aiofiles.open(path, "w") as f:
        await f.write(json.dumps(data, indent=4))
