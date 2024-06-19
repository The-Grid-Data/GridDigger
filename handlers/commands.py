from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

import api
from handlers import FILTER_MAIN
from handlers.utils import generate_applied_filters_text


def start(update: Update, context) -> int:
    update.message.reply_text("Try something cool like 'solana'\n\nOr hit /filter to get started.")
    return -1 #SEARCH_READY


# this filter command should show all results given no text but with applied filters in user_data if any it should
# show a text of the number of results and several buttons first button in the list should be "Show all results",
# another one should be "Inc search", this one should toggle whether the search is for profile titles only or
# including descriptions. finally, show four buttons for each filter type {profile filters, product filters,
# entity filters, assets filters}, list each two a row
# finally, create a button handler for when the user selects a filter type or just the "Show all results" button or
def filter(update: Update, context) -> int:
    user_data = context.user_data
    results_count = len(api.get_profiles(user_data))  # Assuming get_profiles function takes user_data and returns results
    user_data["profileNameSearch"] = {}

    # Limit the number of results shown on the button text to 20
    display_results_count = min(results_count, 20)

    # Create buttons
    keyboard_buttons = [
        [InlineKeyboardButton('🟢Profile filters', callback_data='profile_filters'),
         InlineKeyboardButton('🟢Product filters', callback_data='product_filters')],
        [InlineKeyboardButton('🟢Asset filters', callback_data='asset_filters'),
         InlineKeyboardButton('🟢Entity filters', callback_data='entity_filters')],
        [InlineKeyboardButton('🔄Reset Filters', callback_data='reset_all'),
         InlineKeyboardButton('🔘Inc search', callback_data='inc_search')]
    ]

    # Add "Show profiles" button if results_count > 0
    if results_count > 0:
        keyboard_buttons.insert(0, [InlineKeyboardButton(f'Show profiles ({display_results_count})', callback_data='show')])

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

    # Send the filter message
    update.message.reply_text(f"Applied filters: {generate_applied_filters_text(user_data)}\nFound results: {results_count}", reply_markup=keyboard)
    return FILTER_MAIN





def help_command(update: Update, context) -> None:
    update.message.reply_text("Use /start to test this bot.")


