import os
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
APP_URL = os.environ.get("APP_URL")  # e.g., https://yourapp.onrender.com

app = Flask(__name__)

# Define a simple /start handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I am alive and running!")

# Create the bot app
application = ApplicationBuilder().token(BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))

# Flask route for Telegram webhook
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.process_update(update)
    return "OK"

# Route to verify it's up
@app.route("/", methods=["GET"])
def index():
    return "🤖 Nadregator Bot is up!"

# Webhook setup on start
async def set_webhook():
    webhook_url = f"{APP_URL}/{BOT_TOKEN}"
    await application.bot.set_webhook(url=webhook_url)

if __name__ == "__main__":
    import asyncio

    # Set webhook before running Flask
    asyncio.run(set_webhook())
    app.run(host="0.0.0.0", port=10000)
