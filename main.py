import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
)

# Get the Telegram token and webhook URL from environment
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # e.g. https://your-app.onrender.com/webhook

# Create Flask app
flask_app = Flask(__name__)

# Create the bot application
application = ApplicationBuilder().token(BOT_TOKEN).build()

# Command handler example
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I'm alive.")

# Add command handlers
application.add_handler(CommandHandler("start", start))

# Flask route to handle Telegram webhook
@flask_app.route("/webhook", methods=["POST"])
async def webhook() -> str:
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return "OK"

# Function to set the webhook
async def set_webhook():
    await asyncio.sleep(3)  # small delay to ensure server is up
    await application.bot.set_webhook(url=WEBHOOK_URL)
    print(f"✅ Webhook set to {WEBHOOK_URL}")

# Run both Flask and webhook setup
if __name__ == "__main__":
    # Set the webhook before starting the Flask server
    asyncio.run(set_webhook())

    # Run the Flask app
    flask_app.run(host="0.0.0.0", port=10000)
