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
def home():
    return "🤖 Nadregator Bot is up!"

# /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! Nadregator Bot is running.")

# Async bot startup
async def run_telegram_bot():
    if not BOT_TOKEN:
        logging.error("❌ BOT_TOKEN is not set. Telegram bot will not start.")
        return

    try:
        application = ApplicationBuilder().token(BOT_TOKEN).build()
        application.add_handler(CommandHandler("start", start))

        logging.info("✅ Telegram bot is starting...")
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        logging.info("✅ Bot polling started.")
        await application.updater.idle()
    except Exception as e:
        logging.exception(f"❌ Failed to start bot: {e}")

# Main app runner
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(run_telegram_bot())
    app.run(host="0.0.0.0", port=10000)

