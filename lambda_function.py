import os
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Initialize the bot with the token
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text('Hi!')


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)


def lambda_handler(event, context):
    """Handle incoming webhook requests from Telegram."""
    application = Application.builder().token(TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Process the event from the webhook
    update = Update.de_json(json.loads(event["body"]), application.bot)
    application.update_queue.put(update)

    return {
        "statusCode": 200,
        "body": json.dumps({"status": "ok"})
    }


if __name__ == "__main__":
    pass
    # For local testing
    # from telegram.ext import Updater
    #
    # updater = Updater(TOKEN)
    # updater.dispatcher.add_handler(CommandHandler("start", start))
    # updater.dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    #
    # updater.start_polling()
    # updater.idle()
