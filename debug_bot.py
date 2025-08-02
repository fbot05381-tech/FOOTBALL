from telegram.ext import ApplicationBuilder
from telegram import Update
import logging

logging.basicConfig(level=logging.INFO)

TOKEN = "7496362823:AAHpnck9YF3HmaPU7lYIOqKMD1TfpHirUmE"

async def catch_all(update: Update, context):
    print("📥 RAW UPDATE:", update.to_dict())

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(type("AnyHandler",(object,),{"check_update":lambda s,u:True,"handle_update":catch_all})())
    print("✅ Debug Bot Running...")
    app.run_polling()
