import telegram

TOKEN = "7496362823:AAHpnck9YF3HmaPU7lYIOqKMD1TfpHirUmE"
bot = telegram.Bot(TOKEN)
bot.delete_webhook(drop_pending_updates=True)
print("✅ Webhook Reset Done!")
