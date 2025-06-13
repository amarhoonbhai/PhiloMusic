
import json
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = 'YOUR_BOT_TOKEN'
OWNER_ID = 123456789  # Replace with your Telegram user ID
APPROVED_FILE = 'approved_users.json'

def load_approved():
    try:
        with open(APPROVED_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_approved(data):
    with open(APPROVED_FILE, 'w') as f:
        json.dump(data, f, indent=2)

async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("You are not authorized to use this command.")
        return

    if len(context.args) != 1 or not context.args[0].isdigit():
        await update.message.reply_text("Usage: /approve <user_id>")
        return

    user_id = context.args[0]
    expires = (datetime.utcnow() + timedelta(days=30)).strftime("%Y-%m-%d")
    approved = load_approved()
    approved[user_id] = expires
    save_approved(approved)

    await update.message.reply_text(f"✅ User {user_id} approved until {expires}.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("approve", approve))
    print("Bot is running...")
    app.run_polling()
