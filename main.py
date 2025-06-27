import os
import logging
import asyncio
from flask import Flask
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes
)

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Load token from environment
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable not set")

# Flask app for Render
app = Flask(__name__)

@app.route("/")
def index():
    return "🤖 Nadregator Bot is running!", 200

# Telegram handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I'm Nadregator!")

# Run the bot (in thread-safe asyncio way)
def run_bot():
    asyncio.run(_run_bot_async())

async def _run_bot_async():
    app_ = ApplicationBuilder().token(BOT_TOKEN).build()
    app_.add_handler(CommandHandler("start", start))
    await app_.initialize()
    await app_.start()
    await app_.updater.start_polling()
    await app_.updater.idle()

if __name__ == "__main__":
    import threading
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

