import os

# ✅ Data folder paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
ASSETS_DIR = os.path.join(BASE_DIR, "assets", "gifs")

# ✅ Ensure folders exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

# ✅ JSON data files
PLAYERS_FILE = os.path.join(DATA_DIR, "players.json")
TEAMS_FILE = os.path.join(DATA_DIR, "teams.json")
TOURNAMENTS_FILE = os.path.join(DATA_DIR, "tournaments.json")

# ✅ GIF Assets (make sure files exist in assets/gifs/)
GOAL_GIF = os.path.join(ASSETS_DIR, "goal.gif")
PASS_GIF = os.path.join(ASSETS_DIR, "pass.gif")
DEFENSIVE_GIF = os.path.join(ASSETS_DIR, "defensive.gif")
STEAL_GIF = os.path.join(ASSETS_DIR, "steal.gif")
CELEBRATION_GIF = os.path.join(ASSETS_DIR, "celebration.gif")
SAD_GIF = os.path.join(ASSETS_DIR, "sad.gif")

# ✅ Gameplay Constants
MAX_TEAM_SIZE = 8       # Players per team
ROUNDS = 3              # Match rounds
ROUND_TIME = 15 * 60    # 15 minutes per round (in seconds)
