import asyncio
import threading
from flask import Flask
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
)

# Replace this with your actual bot token
BOT_TOKEN = "YOUR_BOT_TOKEN"

app = Flask(__name__)

@app.route("/")
def index():
    return "🤖 NadRegatorBot is running."

# Basic /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I'm alive.")

# Run Telegram bot logic
async def start_bot():
    try:
        print("🚀 Bot initializing...")
        application = ApplicationBuilder().token(BOT_TOKEN).build()

        # Add command handlers
        application.add_handler(CommandHandler("start", start))

        await application.initialize()
        await application.start()
        await application.updater.start_polling()

        print("✅ Bot polling started.")
    except Exception as e:
        print(f"❌ Bot failed to start: {e}")

# Run bot in its own thread to avoid event loop conflicts
def run_bot():
    asyncio.run(start_bot())

if __name__ == "__main__":
    print("🔧 main.py is running")
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()

    # Run Flask app (should be served by Hypercorn, not directly in prod)
    app.run(host="0.0.0.0", port=10000)

