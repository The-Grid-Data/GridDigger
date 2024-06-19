from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
import api
from handlers import utils, FILTER_MAIN
from handlers.filters import show_sub_filters, show_filters_main_menu
from handlers.utils import show_profiles


def handle_filter_main_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    query.answer()
    data = context.user_data

    if query.data == "show":
        return show_profiles(data, update, context)
    if query.data.startswith('reset'):
        if utils.reset_filters(data):
            return show_filters_main_menu(update, context)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Already reset")
            return FILTER_MAIN
    if query.data == 'inc_search':
        utils.toggle_inc_search(data)
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Inc search: {data['inc_search']}\n"
                                                                              f"\nEnabling this will search for both "
                                                                              f"profile titles and descriptions.")
        return FILTER_MAIN
    if query.data.endswith("_filters"):
        filter_type = query.data.split("_")[0]
        data['filter_type'] = {}  # to avoid stupid errors
        data['filter_type'] = filter_type

        print("query.data", query.data)
        print("filter_type", filter_type)

        return show_sub_filters(update, context)
    return ConversationHandler.END


def expand_profile_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    query.answer()

    # Extract profile ID from the callback data
    profile_id = query.data.split('_')[1]

    # Fetch the full profile data
    profile_data = api.get_full_profile_data_by_id(profile_id)

    # Construct full profile message text
    message_text = f"*Name:* {profile_data['name']}\n"
    message_text += f"*Sector:* {profile_data['profileSector']['name'] if profile_data.get('profileSector') else 'N/A'}\n"
    message_text += f"*Main Product Type:* {', '.join([product['name'] for product in profile_data.get('products', [])])}\n"
    message_text += f"*Issued Assets:* {', '.join([asset['name'] for asset in profile_data.get('assets', [])])}\n"
    message_text += f"*Tag Line:* {profile_data.get('tagLine', 'N/A')}\n"
    message_text += f"*Description:* {profile_data.get('descriptionShort', 'N/A')}\n"

    buttons = []
    if profile_data.get('urlMain'):
        buttons.append([InlineKeyboardButton("Website", url=profile_data['urlMain'])])
    if profile_data.get('urlDocumentation'):
        buttons.append([InlineKeyboardButton("Documentation", url=profile_data['urlDocumentation'])])
    if profile_data.get('socials'):
        for social in profile_data['socials']:
            buttons.append([InlineKeyboardButton("Social", url=social['url'])])
    reply_markup = InlineKeyboardMarkup(buttons) if buttons else None

    # Check if the original message has an image
    if message_contains_media(query.message):
        # Update the caption for a media message
        query.edit_message_caption(caption=message_text, parse_mode='Markdown', reply_markup=reply_markup)
    else:
        # Update the text for a non-media message
        query.edit_message_text(text=message_text, parse_mode='Markdown', reply_markup=reply_markup)


def message_contains_media(message):
    # print("message", message)
    # print("message photo", message.photo)
    return bool(message.photo)

