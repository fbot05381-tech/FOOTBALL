# ⚽ Telegram Football Game Bot

A fully interactive Telegram football game bot with **Team Mode** & **Tournament Mode**, referee system, goalkeeper mechanics, 3-round matches, GIF animations, and MVP tracking.

---

## 🚀 Features
✅ `/start_football` → Choose Team Mode or Tournament Mode  
✅ **Team Mode:**  
- Referee system with "I'm the referee" button  
- `/create_team` → Create Team A & B  
- `/join_A` & `/join_B` → Players join teams (max 8 per team)  
- `/captain <A/B> <player_id>` → Set team captain  
- `/gk <A/B> <player_id>` → Set goalkeeper  
- `/change_GK <A/B> <player_id>` → Change goalkeeper  
- `/start_match` → Start 3-round match with coin toss and gameplay  

✅ **Gameplay:**  
- Heads/Tails toss between captains  
- Ball possession with buttons: **KICK**, **DEFENSIVE**, **PASS**  
- Penalty shootouts with number guessing  
- GIF animations (goal, pass, defensive, steal, celebration, sad)  
- MVP tracking based on goals, steals & passes  

✅ **Tournament Mode:**  
- `/create_tournament` → Create tournament (Owner)  
- `/total_team <4-10>` → Set number of teams  
- `/team_members <min-max>` → Set players per team  
- `/register_team <TeamName> <CaptainUsername>` → Register teams  
- `/generate_schedule` → Auto match fixtures  
- `/points_table` → Auto ranking  

✅ **Other:**  
- JSON-based storage (no external DB needed)  
- Render-ready with Procfile & requirements.txt  

---

## 📂 Folder Structure

Football-Bot/ │── bot.py │── config.py │── Procfile │── requirements.txt │── README.md │ ├── handlers/ │   │── start.py │   │── team_mode.py │   │── tournament_mode.py │   │── referee.py │   │── gameplay.py │   │── utils.py │ ├── data/ │   │── players.json │   │── teams.json │   │── tournaments.json │ └── assets/ └── gifs/ │── goal.gif │── pass.gif │── defensive.gif │── steal.gif │── celebration.gif │── sad.gif
