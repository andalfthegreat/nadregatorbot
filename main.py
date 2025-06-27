import os
import asyncio
from flask import Flask
from telegram.ext import ApplicationBuilder, CommandHandler

BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running."

async def start(update, context):
    await update.message.reply_text("Hello, I am alive!")

async def run_bot():
    app_builder = ApplicationBuilder().token(BOT_TOKEN)
    application = app_builder.build()
    application.add_handler(CommandHandler("start", start))
    await application.initialize()
    await application.start()
    print("Bot started.")
    await application.updater.start_polling()
    await application.updater.idle()

if __name__ == "__main__":
    # Start the bot loop without using asyncio.run inside a thread
    loop = asyncio.get_event_loop()
    loop.create_task(run_bot())

    # Run Flask app (this blocks the main thread)
    app.run(host="0.0.0.0", port=10000)
