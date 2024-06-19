import logging
import logging.config
import os
import sys
from telegram.ext import MessageHandler, Updater, CallbackQueryHandler


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv

from handlers.setup import setup

# Load environment variables from a .env file
load_dotenv("bot/.env")


def error(update, context):
    """Log Errors caused by Updates."""

    logging.warning('Update "%s" ', update)
    logging.exception(context.error)



def main():
    updater = Updater(DefaultConfig.TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    # setup
    setup(dp)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    if DefaultConfig.MODE == "webhook":
        updater.start_webhook(
            listen="0.0.0.0",
            port=int(DefaultConfig.PORT),
            url_path=DefaultConfig.TELEGRAM_TOKEN,
            webhook_url=DefaultConfig.WEBHOOK_URL + '/' + DefaultConfig.TELEGRAM_TOKEN
        )

        logging.info(f"Start webhook mode on port {DefaultConfig.PORT}")
    else:
        updater.start_polling()
        logging.info(f"Start polling mode")

    updater.idle()


class DefaultConfig:
    PORT = int(os.environ.get("PORT", 5000))
    TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    MODE = os.environ.get("MODE", "webhook")
    WEBHOOK_URL = os.environ.get("LAMBDA_WEBHOOK_URL", "https://427e-219-92-138-126.ngrok-free.app")
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()

    @staticmethod
    def init_logging():
        logging.basicConfig(
            format="%(asctime)s - %(levelname)s - %(message)s",
            level=DefaultConfig.LOG_LEVEL,
        )


if __name__ == "__main__":
    # Enable logging
    DefaultConfig.init_logging()
    logging.info(f"PORT: {DefaultConfig.PORT}")
    main()
    # API.run_API()