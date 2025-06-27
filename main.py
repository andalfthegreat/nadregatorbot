import os
import logging
from flask import Flask
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes
)

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Get bot token from environment variable
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set!")

# Create a basic Flask app to keep Render Web Service alive
app = Flask(__name__)

@app.route('/')
def index():
    return "🤖 Nadregator Bot is running!", 200

# Define your Telegram bot command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I’m alive!")

def run_bot():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    # Start the bot in a background task so Flask can also run
    application.run_polling(stop_signals=None)

if __name__ == '__main__':
    import threading
    # Start the bot in a separate thread
    threading.Thread(target=run_bot).start()
    # Start Flask app
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
