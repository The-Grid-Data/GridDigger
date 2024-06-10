from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from api import get_profiles

SEARCH_READY, MAIN_FILTERS_MENU, SUB_FILTERS_MENU, TYPING, SEARCH_RESULTS = range(5) # redundant but works


async def search_profiles_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    data = context.user_data
    data["profileNameSearch"] = {}
    data["profileNameSearch"] = update.message.text

    # todo apply filters here

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Show all', callback_data='show_results')],
        #[InlineKeyboardButton('Show results', callback_data='show_results')],
    ])

    results = get_profiles(data)
    results_count = len(results)

    await update.message.reply_text(f"Found {results_count} results:", reply_markup=keyboard)
    print("hi mom")
    return SEARCH_RESULTS


async def start_over_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.edit_message_text(f"This menu has expired, start over please. /filters")
    return ConversationHandler.END

