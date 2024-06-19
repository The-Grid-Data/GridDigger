import json
import os
import logging
from telegram import Update
from telegram.ext import CommandHandler, Application, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text("Hi! This is a simple bot running on AWS Lambda.")

async def handle_update(event, context) -> None:
    """Handle incoming Telegram updates."""
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))

    try:
        update = Update.de_json(json.loads(event["body"]), application.bot)
        await application.process_update(update)
    except Exception as e:
        logger.error(f"Error processing update: {e}")

