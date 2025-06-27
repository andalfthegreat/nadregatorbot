import os
import threading
import asyncio

from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Get the token from environment variable
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Flask app
app = Flask(__name__)

@app.route("/")
def home():
    return "🤖 Nadregator Bot is up!"

# Telegram command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I'm alive.")

# Async bot runner
async def _run_bot():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    await application.run_polling()

# Start the bot in a background thread
def run_bot():
    asyncio.run(_run_bot())

threading.Thread(target=run_bot).start()

# Run Flask (Render will start this as the main process)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)


