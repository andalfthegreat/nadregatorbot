import os
import asyncio
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Load token from environment variable
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# --- Flask setup ---
app = Flask(__name__)

@app.route("/")
def index():
    return "NadregatorBot is running!"

# --- Telegram handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I am NadregatorBot.")

# --- Telegram bot setup ---
async def run_bot():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    await application.run_polling()

# --- Run both Flask and Telegram bot ---
if __name__ == "__main__":
    # Start Telegram bot in a background thread to avoid event loop issues
    threading.Thread(target=lambda: asyncio.run(run_bot()), daemon=True).start()

    # Run the Flask server
    app.run(host="0.0.0.0", port=10000)
