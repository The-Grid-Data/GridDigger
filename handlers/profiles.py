from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest
from telegram.ext import ContextTypes, ConversationHandler
import api
from handlers import utils, FILTER_MAIN
from handlers.filters import show_sub_filters, show_filters_main_menu
from handlers.utils import show_profiles


# Define a function to split the message text
def split_message(text, max_length):
    return [text[i:i + max_length] for i in range(0, len(text), max_length)]

# Maximum length for Telegram media captions
MAX_CAPTION_LENGTH = 1024

def handle_filter_main_callback(update: Update, context) -> int:
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

        context.bot.send_message(chat_id=update.effective_chat.id, text=f"\nEnabling this will search for both profile titles and descriptions.")
        return show_filters_main_menu(update, context)
    if query.data.endswith("_filters"):
        filter_type = query.data.split("_")[0]
        data['filter_type'] = {}  # to avoid stupid errors
        data['filter_type'] = filter_type

        print("query.data", query.data)
        print("filter_type", filter_type)

        return show_sub_filters(update, context)
    return ConversationHandler.END


def expand_profile_callback(update: Update, Context):
    query = update.callback_query
    query.answer()

    # Extract profile ID from the callback data
    profile_id = query.data.split('_')[1]

    # Fetch the full profile data
    profile_data = api.get_full_profile_data_by_id(profile_id)

    # Construct full profile message text
    message_text = f"*ID:* {profile_data['id']}\n"
    message_text += f"*Name:* {profile_data['name']}\n"
    message_text += f"*Sector:* {profile_data['profileSector']['name'] if profile_data.get('profileSector') else '-'}\n"
    message_text += f"*Type:* {profile_data['profileType']['name'] if profile_data.get('profileType') else '-'}\n"
    message_text += f"*Status:* {profile_data['profileStatus']['name'] if profile_data.get('profileStatus') else '-'}\n"
    message_text += f"*Founding Date:* {profile_data.get('foundingDate', '-')}\n"
    message_text += f"*Slug:* {profile_data.get('slug', '-')}\n"
    #message_text += f"*Description:* {profile_data.get('descriptionShort', '-')}\n" it might get too long (telegram.error.BadRequest: Media_caption_too_long)
    message_text += f"*Long Description:* {profile_data.get('descriptionLong', '-')}\n"
    message_text += f"*Tag Line:* {profile_data.get('tagLine', '-')}\n"
    message_text += f"*Main Product Type:* {', '.join([product['name'] for product in profile_data.get('products', [])])}\n" # you may remove this
    message_text += f"*Issued Assets:* {', '.join([asset['name'] for asset in profile_data.get('assets', [])])}\n"


    buttons = []
    if profile_data.get('urlMain'):
        buttons.append([InlineKeyboardButton("Website", url=profile_data['urlMain'])])
    if profile_data.get('urlDocumentation'):
        buttons.append([InlineKeyboardButton("Documentation", url=profile_data['urlDocumentation'])])
    if profile_data.get('urlWhitepaper'):
        buttons.append([InlineKeyboardButton("Whitepaper", url=profile_data['urlWhitepaper'])])
    if profile_data.get('urlBlog'):
        buttons.append([InlineKeyboardButton("Blog", url=profile_data['urlBlog'])])
    if profile_data.get('socials'):
        for social in profile_data['socials']:
            buttons.append([InlineKeyboardButton('Social', url=social['url'])])
    reply_markup = InlineKeyboardMarkup(buttons) if buttons else None

    # Check if the original message has an image
    if message_contains_media(query.message):
        if len(message_text) > MAX_CAPTION_LENGTH:
            # Split the message text if it's too long
            messages = split_message(message_text, MAX_CAPTION_LENGTH)

            try:
                # Update the caption for a media message with the first part
                initial_message = query.edit_message_caption(caption=messages[0], parse_mode='Markdown',
                                                             reply_markup=reply_markup)
                # Send the remaining parts as separate messages
                for part in messages[1:]:
                    query.message.reply_text(text=part, parse_mode='Markdown',
                                             reply_to_message_id=initial_message.message_id)
            except BadRequest as e:
                if "Media_caption_too_long" in str(e):
                    # Handle the specific error if needed
                    raise e
        else:
            # Update the caption if it's within the limit
            query.edit_message_caption(caption=message_text, parse_mode='Markdown', reply_markup=reply_markup)
    else:
        try:
            # Update the text for a non-media message
            query.edit_message_text(text=message_text, parse_mode='Markdown', reply_markup=reply_markup)
        except BadRequest as e:
            # Handle any errors
            raise e

def message_contains_media(message):
    # print("message", message)
    # print("message photo", message.photo)
    return bool(message.photo)

