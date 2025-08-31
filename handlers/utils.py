import os
import re
from urllib.parse import urlparse

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, ContextTypes

import api
from database import increment_fetch_count

# Import enhanced profile service
from services.enhanced_profile_service import enhanced_profile_service

MONITORING_GROUP_ID = os.getenv('MONITORING_GROUP_ID')


def create_main_menu_filter_keyboard(user_data, results_count):
    # Limit the number of results shown on the button text to 20
    display_results_count = min(results_count, 20)

    # Retrieve filters from user data
    filters = user_data.get('FILTERS', {})

    # Determine the appropriate emoji for each filter type
    profile_filter_emoji = "🟡" if 'profileNameSearch' in filters or 'profileType' in filters or 'profileSector' in filters or 'profileStatuses' in filters else '🟢'
    product_filter_emoji = "🟡" if 'productTypes' in filters or 'productStatuses' in filters else '🟢'
    entity_filter_emoji = "🟡" if 'entityTypes' in filters or 'entityName' in filters else '🟢'
    asset_filter_emoji = "🟡" if 'assetTickers' in filters or 'assetTypes' in filters or 'assetStandards' in filters else '🟢'

    solana_toggle_text = "✔️Solana filter" if user_data.get('solana_filter_toggle', True) else "Solana filter"

    # Create buttons
    keyboard_buttons = [
        [InlineKeyboardButton('🔄Reset filters', callback_data='reset_all')],
        [InlineKeyboardButton(f'{profile_filter_emoji}Profile filters', callback_data='profile_filters'),
         InlineKeyboardButton(f'{product_filter_emoji}Product filters', callback_data='product_filters')],
        [InlineKeyboardButton(f'{asset_filter_emoji}Asset filters', callback_data='asset_filters'),
         InlineKeyboardButton(f'{entity_filter_emoji}Entity filters', callback_data='entity_filters')],
        [InlineKeyboardButton(f'{solana_toggle_text}', callback_data='solana_filter_toggle'),
         InlineKeyboardButton(f"{'✔️' if user_data.get('inc_search') else ''}Inc search",
                              callback_data='inc_search')]
    ]

    # Add "Show profiles" button if results_count > 0
    if results_count > 0:
        keyboard_buttons.insert(0, [
            InlineKeyboardButton(f'Show profiles ({display_results_count})', callback_data='show')])

    # Create and return the InlineKeyboardMarkup object
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    return keyboard


async def show_profiles(data, update: Update, context: ContextTypes.DEFAULT_TYPE):
    profiles = api.get_profiles(data)
    
    # Add null safety for profiles
    if profiles is None:
        profiles = []

    increment_fetch_count(update.effective_user.id)
    
    # Send a monitoring message with user details (only if MONITORING_GROUP_ID is set)
    if MONITORING_GROUP_ID:
        user = update.effective_user
        monitoring_message_text = (
            f"User {user.id} ({user.username}) showed "
            f"{min(len(profiles), 20)} of these settings:\n{generate_applied_filters_text(data)}"
        )
        try:
            await context.bot.send_message(
                text=monitoring_message_text,
                chat_id=MONITORING_GROUP_ID
            )
        except Exception as e:
            print(f"Warning: Could not send monitoring message: {e}")
    
    # Determine the correct chat_id and message_id based on update type
    if update.callback_query:
        chat_id = update.callback_query.message.chat.id
        message_id = update.callback_query.message.message_id
    else:
        chat_id = update.effective_chat.id
        message_id = update.effective_message.message_id
    
    # edit the message and remove the buttons
    await context.bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=f"Showing profiles with applied filters: \n\n {generate_applied_filters_text(data)}",
        reply_markup=None
    )
    for profile in profiles[:20]:
        try:
            await send_profile_message(update, context, profile)
        except Exception as e:
            await context.bot.send_message(chat_id=chat_id, text=f"Error: {e}")

    return ConversationHandler.END


async def send_profile_message(update: Update, context: ContextTypes.DEFAULT_TYPE, profile):
    """Enhanced profile message using service layer with products and assets"""
    profile_id = profile['id']
    
    # Use enhanced service to get formatted profile card
    formatted_profile = enhanced_profile_service.get_profile_card(profile_id)
    
    if not formatted_profile:
        # Fallback to basic message if service fails
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"*Profile ID:* {profile_id}\n*Error:* Unable to load profile",
            parse_mode='Markdown'
        )
        return
    
    # Get reply markup from formatted profile
    reply_markup = formatted_profile.get_inline_keyboard_markup()
    
    # Handle media if available
    if formatted_profile.has_media and formatted_profile.media_url:
        logo_url = formatted_profile.media_url
        
        # Check if we can display the image
        if is_valid_url(logo_url) and is_supported_image_format(logo_url):
            await download_and_send_image(
                logo_url,
                update.effective_chat.id,
                formatted_profile.message_text,
                reply_markup,
                context
            )
        else:
            # Send as text message if image can't be displayed
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=formatted_profile.message_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
    else:
        # Send as text message (no media)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=formatted_profile.message_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )


import requests

async def download_and_send_image(url, chat_id, message_text, reply_markup, context):
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        if response.status_code == 200:
            with open('temp_image.png', 'wb') as f:
                f.write(response.content)
            await context.bot.send_photo(chat_id=chat_id, photo=open('temp_image.png', 'rb'), caption=message_text,
                                   parse_mode='Markdown', reply_markup=reply_markup)
        else:
            await context.bot.send_message(chat_id=chat_id, text="Failed to download image.", parse_mode='Markdown', reply_markup=reply_markup)
    except requests.exceptions.RequestException as e:
        await context.bot.send_message(chat_id=chat_id, text=f"Error: {str(e)}", parse_mode='Markdown', reply_markup=reply_markup)



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
    supported_formats = {}#{'.jpg', '.jpeg', '.png'}
    path = urlparse(url).path
    _, ext = os.path.splitext(path)
    return ext.lower() in supported_formats


def is_convertible_image_format(url):
    convertible_formats = {}  # {'.svg', '.webp'} here where you turn it on
    path = urlparse(url).path
    _, ext = os.path.splitext(path)
    return ext.lower() in convertible_formats


# for measuring execution time
# import time
# import psutil


# def convert_image(url):
#     start_time = time.time()
#
#     process = psutil.Process(os.getpid())
#     start_cpu_times = process.cpu_times()
#     start_memory_info = process.memory_info()
#
#     response = requests.get(url)
#     if response.status_code == 200:
#         image_data = response.content
#         path = urlparse(url).path
#         _, ext = os.path.splitext(path)
#         ext = ext.lower()
#
#         if ext == '.svg':
#             png_image = cairosvg.svg2png(bytestring=image_data)
#             result = BytesIO(png_image)
#         elif ext == '.webp':
#             image = Image.open(BytesIO(image_data)).convert("RGB")
#             output = BytesIO()
#             image.save(output, format="PNG")
#             output.seek(0)
#             result = output
#         else:
#             result = None
#
#     else:
#         result = None
#
#     end_time = time.time()
#     end_cpu_times = process.cpu_times()
#     end_memory_info = process.memory_info()
#
#     execution_time = end_time - start_time
#     cpu_time_user = end_cpu_times.user - start_cpu_times.user
#     cpu_time_system = end_cpu_times.system - start_cpu_times.system
#     total_cpu_time = cpu_time_user + cpu_time_system
#     memory_usage = (end_memory_info.rss - start_memory_info.rss) / (1024 * 1024)
#
#     print(f"Execution Time: {execution_time:.2f} seconds, Total CPU Time: {total_cpu_time:.2f} seconds, Memory Usage: {memory_usage:.2f} MB")
#
#     return result
#

#import cairosvg
def convert_image(url):
    # response = requests.get(url)
    # if response.status_code == 200:
    #     image_data = response.content
    #     path = urlparse(url).path
    #     _, ext = os.path.splitext(path)
    #     ext = ext.lower()
    #
    #     if ext == '.svg':
    #         png_image = cairosvg.svg2png(bytestring=image_data)
    #         return BytesIO(png_image)
    #     elif ext == '.webp':
    #         image = Image.open(BytesIO(image_data)).convert("RGB")
    #         output = BytesIO()
    #         image.save(output, format="PNG")
    #         output.seek(0)
    #         return output
    return None


def reset_filters(data) -> bool:
    if data.get('FILTERS'):
        data['FILTERS'] = {}
        return True
    return False


    # print(data)
    # print(data.get('FILTERS'))
    # print("empty FILTERS" if not data.get('FILTERS') or data['FILTERS'] == {} else "FILTERS")
    # if not data.get('FILTERS') or data['FILTERS'] == {}:
    #     return False
    # data['FILTERS'] = {}
    # return True


def generate_applied_filters_text(data):
    data.setdefault("FILTERS", {})

    # Initialize a dictionary to hold filter names and values
    filters_text = {}

    # Iterate through the filters and extract the values
    for key, value in data["FILTERS"].items():
        if not key.endswith('_query'):
            filters_text[key] = value

    # Generate the output text
    result = '\n'.join(f"{key}: {value}" for key, value in filters_text.items())

    return result


def toggle_inc_search(data):
    # # Toggle the 'inc_search' flag
    # if not data['FILTERS']:
    #     data['FILTERS'] = {}

    data.setdefault('inc_search', False)
    data['inc_search'] = not data['inc_search']  # a label on filter menu
    print("inc_search:", data['inc_search'])

def toggle_solana_filter(data):
    # # Toggle the 'inc_search' flag
    # if not data['FILTERS']:
    #     data['FILTERS'] = {}

    data.setdefault('solana_filter_toggle', True)
    data['solana_filter_toggle'] = not data['solana_filter_toggle']  # a label on filter menu
    print("solana_filter_toggle:", data['solana_filter_toggle'])


# some user names have special characters that cause errors.
def escape_markdown(text):
    """Helper function to escape special characters for Markdown."""
    escape_chars = r'\*_`\['
    return re.sub(r'([{}])'.format(escape_chars), r'\\\1', text)
