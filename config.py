import os

DATA_FOLDER = "data"
PLAYERS_FILE = os.path.join(DATA_FOLDER, "players.json")
TEAMS_FILE = os.path.join(DATA_FOLDER, "teams.json")
TOURNAMENTS_FILE = os.path.join(DATA_FOLDER, "tournaments.json")

ASSETS_FOLDER = "assets/gifs"
GOAL_GIF = os.path.join(ASSETS_FOLDER, "goal.gif")
PASS_GIF = os.path.join(ASSETS_FOLDER, "pass.gif")
DEFENSIVE_GIF = os.path.join(ASSETS_FOLDER, "defensive.gif")
STEAL_GIF = os.path.join(ASSETS_FOLDER, "steal.gif")
CELEBRATION_GIF = os.path.join(ASSETS_FOLDER, "celebration.gif")
SAD_GIF = os.path.join(ASSETS_FOLDER, "sad.gif")

os.makedirs(DATA_FOLDER, exist_ok=True)
os.makedirs(ASSETS_FOLDER, exist_ok=True)
