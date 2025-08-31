import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest
from telegram.ext import ContextTypes, ConversationHandler
import api
from database import increment_expand_count
from handlers import utils, FILTER_MAIN
from handlers.filters import show_sub_filters, show_filters_main_menu
from handlers.utils import show_profiles

# Import new enhanced service
from services.enhanced_profile_service import enhanced_profile_service

logger = logging.getLogger(__name__)

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
    """Enhanced expand profile callback using service layer"""
    query = update.callback_query
    await query.answer()

    try:
        # Extract profile ID from the callback data and strip whitespace
        profile_id = query.data.split('_')[1].strip()
        logger.info(f"Expand requested for profile ID: '{profile_id}' from callback data: '{query.data}'")

        # Use enhanced service to get formatted profile
        formatted_profile = enhanced_profile_service.get_expanded_profile(profile_id)

        if not formatted_profile:
            logger.error(f"Enhanced service returned None for profile ID: '{profile_id}'")
            
            # Try fallback to legacy API
            try:
                logger.info(f"Attempting fallback to legacy API for profile ID: '{profile_id}'")
                legacy_data = api.get_full_profile_data_by_id(profile_id)
                
                if legacy_data:
                    logger.info(f"Legacy API has data for profile ID: '{profile_id}', using fallback formatting")
                    
                    # Create a basic fallback message
                    name = legacy_data.get('name', 'Unknown')
                    sector = legacy_data.get('profileSector', {}).get('name', '-') if legacy_data.get('profileSector') else '-'
                    description = legacy_data.get('descriptionLong', legacy_data.get('descriptionShort', '-'))
                    
                    fallback_message = f"*Name:* {name}\n*Sector:* {sector}\n*Description:* {description}"
                    
                    # Create basic buttons from URLs
                    buttons = []
                    urls = legacy_data.get('urls', [])
                    for url_obj in urls[:3]:  # Limit to 3 buttons
                        if url_obj and url_obj.get('url'):
                            url_type = url_obj.get('urlType', {}).get('name', 'Link')
                            buttons.append([InlineKeyboardButton(url_type, url=url_obj['url'])])
                    
                    reply_markup = InlineKeyboardMarkup(buttons) if buttons else None
                    
                    await query.edit_message_text(
                        text=fallback_message + "\n\n_Note: Using fallback formatting_",
                        parse_mode='Markdown',
                        reply_markup=reply_markup
                    )
                    return
                else:
                    logger.info(f"Legacy API also has no data for profile ID: '{profile_id}'")
                    
            except Exception as e:
                logger.error(f"Legacy API also failed for profile ID: '{profile_id}': {e}")
            
            await query.edit_message_text(f"Profile not found or unavailable. (ID: {profile_id})")
            return
            
    except Exception as e:
        logger.error(f"Error in expand_profile_callback: {e}")
        await query.edit_message_text("Error processing expand request.")
        return

    # Increment usage tracking
    increment_expand_count(update.effective_user.id)

    # Get profile name for monitoring (from the formatted message or service)
    profile_data = enhanced_profile_service.get_raw_profile_data(profile_id, full_data=True)
    profile_name = profile_data.name if profile_data else "Unknown"

    # Send a monitoring message with user details (only if MONITORING_GROUP_ID is set)
    if MONITORING_GROUP_ID:
        user = update.effective_user
        user_link = f"[{user.username}](tg://user?id={user.id})" if user.username else f"User {user.id}"
        monitoring_message_text = (
            f"User {user.id} ({user_link}) expanded profile {profile_id} of name {profile_name}"
        )
        try:
            await context.bot.send_message(text=monitoring_message_text, parse_mode='Markdown', chat_id=MONITORING_GROUP_ID)
        except Exception as e:
            print(f"Warning: Could not send monitoring message: {e}")

    # Get the reply markup from formatted profile
    reply_markup = formatted_profile.get_inline_keyboard_markup()

    # Check if the original message has an image
    if message_contains_media(query.message):
        if len(formatted_profile.message_text) > MAX_CAPTION_LENGTH:
            # Split the message text if it's too long
            messages = split_message(formatted_profile.message_text, MAX_CAPTION_LENGTH)

            try:
                # Update the caption for a media message with the first part
                initial_message = await query.edit_message_caption(
                    caption=messages[0],
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
                # Send the remaining parts as separate messages
                for part in messages[1:]:
                    await query.message.reply_text(
                        text=part,
                        parse_mode='Markdown',
                        reply_to_message_id=initial_message.message_id
                    )
            except BadRequest as e:
                if "Media_caption_too_long" in str(e):
                    # Handle the specific error if needed
                    raise e
        else:
            # Update the caption if it's within the limit
            await query.edit_message_caption(
                caption=formatted_profile.message_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
    else:
        try:
            # Update the text for a non-media message
            await query.edit_message_text(
                text=formatted_profile.message_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        except BadRequest as e:
            # Handle any errors
            raise e

def message_contains_media(message):
    # print("message", message)
    # print("message photo", message.photo)
    return bool(message.photo)

