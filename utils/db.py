import json
import os

TEAM_FILE = "database/team_data.json"
TOURNAMENT_FILE = "database/tournament_data.json"

def load_team_data():
    if not os.path.exists(TEAM_FILE):
        return {}
    with open(TEAM_FILE, "r") as f:
        return json.load(f)

def save_team_data(data):
    with open(TEAM_FILE, "w") as f:
        json.dump(data, f, indent=2)

def load_tournament_data():
    if not os.path.exists(TOURNAMENT_FILE):
        return {}
    with open(TOURNAMENT_FILE, "r") as f:
        return json.load(f)

def save_tournament_data(data):
    with open(TOURNAMENT_FILE, "w") as f:
        json.dump(data, f, indent=2)
