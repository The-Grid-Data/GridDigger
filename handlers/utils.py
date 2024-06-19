import os
import re
from urllib.parse import urlparse

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, ContextTypes

import api


async def show_profiles(data, update: Update, context: ContextTypes.DEFAULT_TYPE):
    profiles = api.get_profiles(data)
    # edit the message and remove the buttons
    await context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=update.effective_message.message_id,
        text=f"Showing profiles with applied filters: \n\n {generate_applied_filters_text(data)}",
        reply_markup=None
    )
    for profile in profiles[:20]:
        try:
            await send_profile_message(update, context, profile)
        except Exception as e:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error: {e}")

    return ConversationHandler.END


async def send_profile_message(update: Update, context: ContextTypes.DEFAULT_TYPE, profile):
    profile_id = profile['id']
    profile_data = api.get_profile_data_by_id(profile_id)

    # Construct initial message text with basic profile summary
    message_text = f"*Name:* {profile_data['name']}\n"
    message_text += f"*Sector:* {profile_data['profileSector']['name'] if profile_data.get('profileSector') else 'N/A'}\n"
    message_text += f"*short description:* {profile_data['shortDescription'] if profile_data.get('shortDescription') else 'N/A'}\n"
    # Add the "Expand" button
    buttons = [[InlineKeyboardButton("Expand", callback_data=f"expand_{profile_id}")]]
    reply_markup = InlineKeyboardMarkup(buttons)

    # Check if the logo URL is valid and in a supported format
    logo_url = profile_data.get('logo')
    if logo_url and is_valid_url(logo_url) and is_supported_image_format(logo_url):
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=logo_url, caption=message_text,
                                     parse_mode='Markdown', reply_markup=reply_markup)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message_text, parse_mode='Markdown',
                                       reply_markup=reply_markup)


def is_valid_url(url):
    print("url", url)
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None


def is_supported_image_format(url):
    supported_formats = {'.jpg', '.jpeg', '.png'}
    path = urlparse(url).path
    _, ext = os.path.splitext(path)
    return ext.lower() in supported_formats


def reset_filters(data) -> bool:
    if not data.get('FILTERS'):
        return False
    data['FILTERS'] = {}
    return True

def generate_applied_filters_text(data):
    data.setdefault("FILTERS", {})

    # Initialize a dictionary to hold filter names and values
    filters_text = {}

    # Iterate through the filters and extract the values
    for key, value in data["FILTERS"].items():
        if not key.endswith('_id'):
            filters_text[key] = value

    # Generate the output text
    result = '\n'.join(f"{key}: {value}" for key, value in filters_text.items())

    return result