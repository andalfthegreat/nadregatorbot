import os
import asyncio
import logging
from flask import Flask
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram import Update

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Flask(__name__)

@app.route("/")
def index():
    return "Nadregator Bot is live!"

# Command: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi, I'm alive and running!")

# Telegram bot runner
async def run_telegram_bot():
    if not BOT_TOKEN:
        logging.error("❌ BOT_TOKEN not set in environment variables.")
        return

    try:
        app_bot = ApplicationBuilder().token(BOT_TOKEN).build()
        app_bot.add_handler(CommandHandler("start", start))

        logging.info("✅ Telegram bot is starting...")
        await app_bot.initialize()
        await app_bot.start()
        await app_bot.updater.start_polling()
        logging.info("✅ Bot polling started.")
        await app_bot.updater.idle()
    except Exception as e:
        logging.exception(f"❌ Bot failed to start: {e}")

# Main entry point
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(run_telegram_bot())
    app.run(host="0.0.0.0", port=10000)
