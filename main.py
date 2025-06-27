import os
import asyncio
from flask import Flask
from telegram.ext import ApplicationBuilder, CommandHandler

BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Flask(__name__)

@app.route("/")
def index():
    return "🤖 Nadregator Bot is alive!"

async def start_bot():
    print("🚀 Bot initializing...")
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    async def start(update, context):
        await update.message.reply_text("Hi! I am alive.")

    application.add_handler(CommandHandler("start", start))

    print("✅ Starting bot polling...")
    await application.run_polling()

def main():
    loop = asyncio.get_event_loop()

    # Schedule the bot
    loop.create_task(start_bot())

    # Run the Flask app in the same event loop
    from hypercorn.asyncio import serve
    from hypercorn.config import Config

    config = Config()
    config.bind = ["0.0.0.0:10000"]
    loop.run_until_complete(serve(app, config))

if __name__ == "__main__":
    main()

