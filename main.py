import os
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.ext import Dispatcher, MessageHandler, filters

BOT_TOKEN = os.environ.get("BOT_TOKEN")
APP_URL = os.environ.get("APP_URL")  # e.g. https://your-app.onrender.com

app = Flask(__name__)
application = ApplicationBuilder().token(BOT_TOKEN).build()

# Simple handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I'm alive with webhook!")

application.add_handler(CommandHandler("start", start))

@app.route("/")
def home():
    return "🤖 Nadregator Bot is up!"

# This route handles incoming Telegram updates
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.process_update(update)
    return "ok"

if __name__ == "__main__":
    # Set the webhook when starting the app
    import asyncio
    async def set_webhook():
        await application.bot.set_webhook(f"{APP_URL}/{BOT_TOKEN}")

    asyncio.run(set_webhook())
    app.run(host="0.0.0.0", port=10000)

