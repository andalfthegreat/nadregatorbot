import os
import asyncio
from flask import Flask
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram import Update

BOT_TOKEN = os.environ.get("BOT_TOKEN")

app = Flask(__name__)

@app.route("/")
def index():
    return "Bot is alive."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I'm alive.")

async def run_bot():
    app_builder = ApplicationBuilder().token(BOT_TOKEN)
    application = app_builder.build()

    application.add_handler(CommandHandler("start", start))

    await application.initialize()
    await application.start()
    print("Telegram bot started!")
    await application.updater.start_polling()
    await application.updater.idle()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(run_bot())

    # Flask blocks the main thread, but bot still runs in the loop
    app.run(host="0.0.0.0", port=10000)
