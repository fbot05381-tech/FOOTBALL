from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from utils.db import load_json, save_json

router = Router()
DB_FILE = "database/team_mode.json"

# ✅ End Match with Summary (Referee Only)
@router.message(Command("end_match"))
async def end_match(msg: Message):
    data = load_json(DB_FILE)
    chat_id = str(msg.chat.id)

    if chat_id not in data or "referee" not in data[chat_id]:
        await msg.answer("❌ No active match found!")
        return

    match_data = data[chat_id]
    referee = match_data["referee"]
    user = msg.from_user.username or msg.from_user.first_name

    if user != referee:
        await msg.answer("❌ Only referee can end the match!")
        return

    # ✅ Build Summary
    team_a = match_data.get("team_a", [])
    team_b = match_data.get("team_b", [])
    captain_a = match_data.get("captain_a")
    captain_b = match_data.get("captain_b")
    gk_a = match_data.get("gk_a")
    gk_b = match_data.get("gk_b")

    score_a = match_data.get("score_a", 0)
    score_b = match_data.get("score_b", 0)

    def format_team(team, captain, gk):
        text = ""
        for p in team:
            tag = []
            if p == captain:
                tag.append("(C)")
            if p == gk:
                tag.append("(GK)")
            text += f"• {p} {' '.join(tag)}\n"
        return text if text else "No players"

    summary = (
        f"🏁 <b>Match Ended</b>\n"
        f"👤 Referee: {referee}\n\n"
        f"🏆 <b>Team A</b> ({score_a} goals)\n{format_team(team_a, captain_a, gk_a)}\n"
        f"🏆 <b>Team B</b> ({score_b} goals)\n{format_team(team_b, captain_b, gk_b)}\n"
    )

    await msg.answer(summary)

    # ✅ Clear Match Data
    del data[chat_id]
    save_json(DB_FILE, data)
    await msg.answer("🛑 All match data cleared. Ready for a new game!")
