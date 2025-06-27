import os
import asyncio
from flask import Flask
from telegram.ext import ApplicationBuilder, CommandHandler
from telegram import Update

BOT_TOKEN = os.environ.get("BOT_TOKEN")

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello from Nadregator Bot!"

# Telegram command handler
async def start(update: Update, context):
    await update.message.reply_text("Hi! Nadregator is alive!")

# Background bot loop
async def run_bot():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))

    print("Starting Telegram bot polling...")
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    await application.updater.idle()

# Entrypoint
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(run_bot())  # Run the bot in the background
    app.run(host="0.0.0.0", port=10000)  # Start Flask (blocks main thread)
