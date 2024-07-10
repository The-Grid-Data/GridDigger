from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

import api
import database
from handlers import FILTER_MAIN
from handlers.utils import generate_applied_filters_text, create_main_menu_filter_keyboard


def start(update: Update, context) -> int:
    update.message.reply_text("Try something cool like 'solana'\n\nOr hit /filter to get started.")
    database.add_user(update.effective_user.id)
    return -1 #SEARCH_READY


def filter(update: Update, context) -> int:
    user_data = context.user_data
    user_data.setdefault("FILTERS", {})
    user_data.setdefault("inc_search", False)
    results_count = len(api.get_profiles(user_data))  # Assuming get_profiles function takes user_data and returns results

    user_data["profileNameSearch"] = {}

    keyboard = create_main_menu_filter_keyboard(user_data, results_count)

    # Send the filter message
    update.message.reply_text(f"Applied filters:\n{generate_applied_filters_text(user_data)}\nFound results: {results_count}", reply_markup=keyboard)
    return FILTER_MAIN


def help_command(update: Update, context) -> None:
    update.message.reply_text("Use /start to test this bot.")

