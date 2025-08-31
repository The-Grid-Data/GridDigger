import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest
from telegram.ext import ContextTypes, ConversationHandler
import api
from database import increment_expand_count
from handlers import utils, FILTER_MAIN
from handlers.filters import show_sub_filters, show_filters_main_menu
from handlers.utils import show_profiles

MONITORING_GROUP_ID = os.getenv('MONITORING_GROUP_ID')

# Define a function to split the message text
def split_message(text, max_length):
    return [text[i:i + max_length] for i in range(0, len(text), max_length)]

# Maximum length for Telegram media captions
MAX_CAPTION_LENGTH = 1024

async def handle_filter_main_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    data = context.user_data

    if query.data == "show":
        return await show_profiles(data, update, context)
    if query.data.startswith('reset'):
        if utils.reset_filters(data):
            return await show_filters_main_menu(update, context)
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Already reset")
            return FILTER_MAIN
    if query.data == 'inc_search':
        utils.toggle_inc_search(data)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"\nEnabling this results in searching for both profile titles and descriptions.")
        return await show_filters_main_menu(update, context)

    if query.data.startswith('solana'):
        utils.toggle_solana_filter(data)
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f"\nThis Solana filter is enabled by defualt to only show Solana Profiles. Disabling it results in showing non-Solana profiles as well.")
        return await show_filters_main_menu(update, context)

    if query.data.endswith("_filters"):
        filter_type = query.data.split("_")[0]
        data['filter_type'] = {}  # to avoid stupid errors
        data['filter_type'] = filter_type

        print("query.data", query.data)
        print("filter_type", filter_type)

        return await show_sub_filters(update, context)
    return ConversationHandler.END


async def expand_profile_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Extract profile ID from the callback data
    profile_id = query.data.split('_')[1]

    # Fetch the full profile data
    profile_data = api.get_full_profile_data_by_id(profile_id)

    increment_expand_count(update.effective_user.id)

    # Add null safety for profile_data
    if not profile_data:
        profile_data = {}
    
    # Handle V2 schema structure - profile_data IS the profileInfo (not an array)
    # The get_full_profile_data_by_id function returns the first profileInfo directly
    name = profile_data.get('name', 'Unknown')
    profile_id_display = profile_data.get('id', profile_id)
    slug = profile_data.get('slug', '-')
    
    # Send a monitoring message with user details (only if MONITORING_GROUP_ID is set)
    if MONITORING_GROUP_ID:
        user = update.effective_user
        user_link = f"[{user.username}](tg://user?id={user.id})"
        monitoring_message_text = (
            f"User {user.id} ({user_link}) expanded profile {profile_id} of name {name}"
        )
        try:
            await context.bot.send_message(text=monitoring_message_text, parse_mode='Markdown', chat_id=MONITORING_GROUP_ID)
        except Exception as e:
            print(f"Warning: Could not send monitoring message: {e}")

    # Construct full profile message text using V2 schema structure
    message_text = f"*ID:* {profile_id_display}\n"
    message_text += f"*Name:* {name}\n"
    message_text += f"*Sector:* {profile_data.get('profileSector', {}).get('name', '-') if profile_data.get('profileSector') else '-'}\n"
    message_text += f"*Type:* {profile_data.get('profileType', {}).get('name', '-') if profile_data.get('profileType') else '-'}\n"
    message_text += f"*Status:* {profile_data.get('profileStatus', {}).get('name', '-') if profile_data.get('profileStatus') else '-'}\n"
    message_text += f"*Founding Date:* {profile_data.get('foundingDate', '-')}\n"
    message_text += f"*Slug:* {slug}\n"
    message_text += f"*Long Description:* {profile_data.get('descriptionLong', '-')}\n"
    message_text += f"*Tag Line:* {profile_data.get('tagLine', '-')}\n"
    
    # Handle products array from root
    root_data = profile_data.get('root', {})
    products = root_data.get('products', [])
    
    # Add null safety for products
    if products is not None:
        product_names = [product.get('name', 'Unknown') for product in products if product.get('name')]
    else:
        product_names = []
    message_text += f"*Main Product Type:* {', '.join(product_names) if product_names else '-'}\n"
    
    # Handle assets array from root
    assets = root_data.get('assets', [])
    
    # Add null safety for assets
    if assets is not None:
        asset_names = [asset.get('name', 'Unknown') for asset in assets if asset.get('name')]
    else:
        asset_names = []
    message_text += f"*Issued Assets:* {', '.join(asset_names) if asset_names else '-'}\n"

    # Handle URLs from V2 schema structure
    buttons = []
    urls = profile_data.get('urls', [])
    
    # Add null safety for urls
    if urls is None:
        urls = []
    
    # Create buttons based on URL types
    for url_obj in urls:
        url = url_obj.get('url')
        url_type = url_obj.get('urlType', {}).get('name', '').lower()
        
        if url and url_type:
            if 'website' in url_type or 'main' in url_type:
                buttons.append([InlineKeyboardButton("Website", url=url)])
            elif 'documentation' in url_type or 'docs' in url_type:
                buttons.append([InlineKeyboardButton("Documentation", url=url)])
            elif 'whitepaper' in url_type:
                buttons.append([InlineKeyboardButton("Whitepaper", url=url)])
            elif 'blog' in url_type:
                buttons.append([InlineKeyboardButton("Blog", url=url)])
            elif 'social' in url_type or 'twitter' in url_type or 'telegram' in url_type:
                buttons.append([InlineKeyboardButton("Social", url=url)])
            else:
                # Generic button for other URL types
                buttons.append([InlineKeyboardButton(url_type.title(), url=url)])
    
    reply_markup = InlineKeyboardMarkup(buttons) if buttons else None

    # Check if the original message has an image
    if message_contains_media(query.message):
        if len(message_text) > MAX_CAPTION_LENGTH:
            # Split the message text if it's too long
            messages = split_message(message_text, MAX_CAPTION_LENGTH)

            try:
                # Update the caption for a media message with the first part
                initial_message = await query.edit_message_caption(caption=messages[0], parse_mode='Markdown',
                                                             reply_markup=reply_markup)
                # Send the remaining parts as separate messages
                for part in messages[1:]:
                    await query.message.reply_text(text=part, parse_mode='Markdown',
                                             reply_to_message_id=initial_message.message_id)
            except BadRequest as e:
                if "Media_caption_too_long" in str(e):
                    # Handle the specific error if needed
                    raise e
        else:
            # Update the caption if it's within the limit
            await query.edit_message_caption(caption=message_text, parse_mode='Markdown', reply_markup=reply_markup)
    else:
        try:
            # Update the text for a non-media message
            await query.edit_message_text(text=message_text, parse_mode='Markdown', reply_markup=reply_markup)
        except BadRequest as e:
            # Handle any errors
            raise e

def message_contains_media(message):
    # print("message", message)
    # print("message photo", message.photo)
    return bool(message.photo)

