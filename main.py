import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from init_db import create_tables

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! I'm alive and connected to PostgreSQL!")

async def run_bot():
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_TOKEN is not set. Check your environment variables.")

    # Create DB tables if they don't exist
    create_tables()

    # Set up Telegram bot
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))

    # Run bot with polling
    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(run_bot())
