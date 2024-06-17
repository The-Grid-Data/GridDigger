from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

import api
from handlers import FILTER_MAIN
from handlers.filters import generate_applied_filters_text


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Try something cool like 'solana'\n\nOr hit /filter to get started.")
    return -1 #SEARCH_READY


# this filter command should show all results given no text but with applied filters in user_data if any it should
# show a text of the number of results and several buttons first button in the list should be "Show all results",
# another one should be "Inc search", this one should toggle whether the search is for profile titles only or
# including descriptions. finally, show four buttons for each filter type {profile filters, product filters,
# entity filters, assets filters}, list each two a row
# finally, create a button handler for when the user selects a filter type or just the "Show all results" button or
async def filter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_data = context.user_data
    results_count = len(api.get_profiles(user_data))  # Assuming get_profiles function takes user_data and returns results
    user_data["profileNameSearch"] = {}

    # Create buttons
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(f'Show profiles ({results_count})', callback_data='show')],
        [InlineKeyboardButton('🟡Profile filters', callback_data='profile_filters'),
         InlineKeyboardButton('🟢Product filters', callback_data='product_filters')],
        [InlineKeyboardButton('🟢Asset filters', callback_data='asset_filters'),
         InlineKeyboardButton('🟢Entity filters', callback_data='entity_filters')],
        [InlineKeyboardButton('🔄Reset Filters', callback_data='reset_all'),
         InlineKeyboardButton('🔘Inc search', callback_data='inc_search')]
    ])

    # Send the filter message
    await update.message.reply_text(f"Applied filtres: {generate_applied_filters_text(user_data)}", reply_markup=keyboard)
    return FILTER_MAIN




async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Use /start to test this bot.")


