import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

import api
from api import get_profiles
import re
from urllib.parse import urlparse
import os


async def query_result_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    data = context.user_data
    results = get_profiles(data)

    sample_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('more', callback_data='more')],
        #[InlineKeyboardButton('Show results', callback_data='show_results')],
    ])
    if query.data == "show_results":
        #await query.edit_message_text("Here are your results: TODO :)")
        for profile in results:
            try:
                await send_profile_message(update, context, profile)
            except Exception as e:
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Failed to fetch profile {profile['name']}.\n Error: {e}")
        return ConversationHandler.END
    return ConversationHandler.END


def is_valid_url(url):
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


async def send_profile_message(update: Update, context: ContextTypes.DEFAULT_TYPE, profile):
    profile_id = profile['id']
    profile_data = api.get_profile_data_by_id(profile_id)

    # Construct initial message text with basic profile summary
    message_text = f"*Name:* {profile_data['name']}\n"
    message_text += f"*Sector:* {profile_data['profileSector']['name'] if profile_data.get('profileSector') else 'N/A'}\n"

    # Add the "Expand" button
    buttons = [[InlineKeyboardButton("Expand", callback_data=f"expand_{profile_id}")]]
    reply_markup = InlineKeyboardMarkup(buttons)

    # Check if the logo URL is valid and in a supported format
    logo_url = profile_data.get('logo')
    if logo_url and is_valid_url(logo_url) and is_supported_image_format(logo_url):
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=logo_url, caption=message_text, parse_mode='Markdown', reply_markup=reply_markup)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=message_text, parse_mode='Markdown', reply_markup=reply_markup)


async def expand_profile_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

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

    # Update the message with full profile details
    await query.edit_message_text(text=message_text, parse_mode='Markdown', reply_markup=reply_markup)
