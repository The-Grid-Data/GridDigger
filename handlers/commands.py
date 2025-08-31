from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

import api
import database
from handlers import FILTER_MAIN
from handlers.utils import generate_applied_filters_text, create_main_menu_filter_keyboard


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    txt = open("handlers/long_messages/start.txt", "r").read()
    await update.message.reply_text(txt)
    database.add_user(update.effective_user.id)
    return -1 #SEARCH_READY


async def filter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_data = context.user_data
    user_data.setdefault("FILTERS", {})
    user_data.setdefault("inc_search", False)
    results = api.get_profiles(user_data) or []
    results_count = len(results)  # Ensure results are handled safely

    user_data["profileNameSearch"] = {}

    keyboard = create_main_menu_filter_keyboard(user_data, results_count)

    # Send the filter message
    await update.message.reply_text(f"Applied filters:\n{generate_applied_filters_text(user_data)}\nFound results: {results_count}", reply_markup=keyboard)
    return FILTER_MAIN

async def open_source_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    txt = open("handlers/long_messages/open_source.txt", "r").read()
    await update.message.reply_text(txt)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    txt = open("handlers/long_messages/help.txt", "r").read()
    await update.message.reply_text(txt)

