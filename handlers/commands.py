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
    
    # Get total profile count for first-time users
    total_profiles = api.get_total_profile_count()
    
    results = api.get_profiles(user_data) or []
    results_count = len(results)  # Ensure results are handled safely

    user_data["profileNameSearch"] = {}

    keyboard = create_main_menu_filter_keyboard(user_data, results_count)

    # Enhanced message with better UX guidance
    if not user_data.get("FILTERS") or all(not v for v in user_data["FILTERS"].values()):
        # First time or no filters applied
        message = f"🔍 **Profile Search & Filter**\n\n"
        message += f"📊 **{total_profiles:,} profiles** available to search\n\n"
        message += f"**How to search:**\n"
        message += f"• Type any text to search profile names\n"
        message += f"• Use filter buttons below for advanced filtering\n"
        message += f"• Toggle between Quick/Deep search modes\n\n"
        message += f"**Current filters:** None\n"
        message += f"**Found results:** {results_count:,}"
    else:
        # Filters are applied
        message = f"🔍 **Profile Search Results**\n\n"
        message += f"**Applied filters:**\n{generate_applied_filters_text(user_data)}\n\n"
        message += f"**Found results:** {results_count:,} of {total_profiles:,} total profiles"

    # Send the filter message
    await update.message.reply_text(message, reply_markup=keyboard, parse_mode='Markdown')
    return FILTER_MAIN

async def open_source_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    txt = open("handlers/long_messages/open_source.txt", "r").read()
    await update.message.reply_text(txt)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    txt = open("handlers/long_messages/help.txt", "r").read()
    await update.message.reply_text(txt)

