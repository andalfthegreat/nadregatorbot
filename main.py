import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler
from flask import Flask
import threading
import os

# Telegram bot setup
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")

app = ApplicationBuilder().token(BOT_TOKEN).build()

# Add a test command
async def start(update, context):
    await update.message.reply_text("Bot is alive!")

app.add_handler(CommandHandler("start", start))

# Dummy Flask server to keep Render Web Service happy
flask_app = Flask(__name__)

@flask_app.route("/")
def index():
    return "OK", 200

# Start Flask in a separate thread
def run_flask():
    flask_app.run(host="0.0.0.0", port=10000)

# Start Telegram bot
async def run_bot():
    await app.run_polling()

if __name__ == "__main__":
    # Start Flask server (for Render port binding)
    threading.Thread(target=run_flask).start()

    # Run the bot
    asyncio.run(run_bot())
