import os
import asyncio
from flask import Flask
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram import Update

BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Flask(__name__)

@app.route("/")
def home():
    return "🤖 Nadregator Bot is up!"

# Example command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello from Nadregator Bot!")

async def run_bot():
    print("✅ Starting Telegram bot...")
    app_builder = ApplicationBuilder().token(BOT_TOKEN)
    application = app_builder.build()

    application.add_handler(CommandHandler("start", start))

    await application.initialize()
    await application.start()
    print("✅ Bot polling started.")
    await application.updater.start_polling()
    await application.updater.idle()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(run_bot())  # ✅ Start the bot
    app.run(host="0.0.0.0", port=10000)  # ✅ Start Flask
