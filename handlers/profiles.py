import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest
from telegram.ext import ContextTypes, ConversationHandler
import api
from database import increment_expand_count
from handlers import utils, FILTER_MAIN
from handlers.filters import show_sub_filters, show_filters_main_menu
from handlers.utils import show_profiles, generate_applied_filters_text, is_valid_url, is_supported_image_format, download_and_send_image

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
    if query.data == 'toggle_search_mode':
        search_mode_active = utils.toggle_search_mode(data)
        
        if search_mode_active:
            feedback_text = (
                "🔍 **Deep Search Mode Activated**\n\n"
                "✅ **Now searching:** Profile names AND descriptions\n"
                "📈 **Result scope:** More comprehensive results\n"
                "⏱️ **Speed:** Slightly slower but more thorough\n\n"
                "💡 *Perfect for finding profiles by keywords in descriptions*"
            )
        else:
            feedback_text = (
                "📝 **Quick Search Mode Activated**\n\n"
                "✅ **Now searching:** Profile names only\n"
                "⚡ **Result scope:** Faster, focused results\n"
                "🎯 **Speed:** Very fast response\n\n"
                "💡 *Perfect for finding profiles when you know the name*"
            )
        
        await context.bot.send_message(chat_id=update.effective_chat.id, text=feedback_text, parse_mode='Markdown')
        return await show_filters_main_menu(update, context)

    # Solana filter callback removed as part of Phase 1 UX improvements

    if query.data.endswith("_filters"):
        filter_type = query.data.split("_")[0]
        data['filter_type'] = {}  # to avoid stupid errors
        data['filter_type'] = filter_type

        print("query.data", query.data)
        print("filter_type", filter_type)

        return await show_sub_filters(update, context)
    return ConversationHandler.END


async def load_more_profiles_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Load More profiles callback for pagination"""
    query = update.callback_query
    await query.answer()
    
    try:
        data = context.user_data
        
        # Check if pagination state exists
        if 'pagination' not in data:
            await query.edit_message_text("Pagination state not found. Please start a new search.")
            return
        
        pagination = data['pagination']
        current_offset = pagination['current_offset']
        batch_size = pagination['batch_size']
        total_results = pagination['total_results']
        all_profiles = pagination.get('all_profiles', [])
        
        # Calculate next batch
        new_offset = current_offset + batch_size
        end_offset = min(new_offset + batch_size, total_results)
        
        # Check if there are more profiles to load
        if new_offset >= total_results:
            await query.edit_message_text("No more profiles to load.")
            return
        
        # Update pagination state
        pagination['current_offset'] = new_offset
        
        # Get profiles for this batch
        profiles_to_show = all_profiles[new_offset:end_offset]
        
        # Update the message with new pagination info
        filter_text = generate_applied_filters_text(data)
        
        if filter_text and filter_text != "No filters applied":
            message = f"🔍 **Showing filtered profiles**\n\n**Applied filters:**\n{filter_text}\n\n**Displaying:** {new_offset + 1}-{end_offset} of {total_results:,} matching profiles"
        else:
            message = f"📋 **Showing all profiles**\n\n**Displaying:** {new_offset + 1}-{end_offset} of {total_results:,} total profiles"
        
        # Add "Load More" button if there are still more results
        reply_markup = None
        if end_offset < total_results:
            remaining = total_results - end_offset
            load_more_button = InlineKeyboardButton(
                f"📄 Load More ({remaining} remaining)",
                callback_data='load_more_profiles'
            )
            reply_markup = InlineKeyboardMarkup([[load_more_button]])
            message += f"\n\n💡 *Click 'Load More' to see the next {min(batch_size, remaining)} profiles*"
        else:
            message += f"\n\n✅ *All {total_results:,} profiles have been loaded*"
        
        # Update the message
        await query.edit_message_text(
            text=message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        # Send the new batch of profiles
        chat_id = query.message.chat.id
        for profile in profiles_to_show:
            try:
                await send_profile_message_direct(chat_id, context, profile)
            except Exception as e:
                await context.bot.send_message(chat_id=chat_id, text=f"Error loading profile: {e}")
        
        # Send monitoring message if enabled
        if MONITORING_GROUP_ID:
            user = update.effective_user
            monitoring_message_text = (
                f"User {user.id} ({user.username}) loaded more profiles "
                f"(batch {new_offset + 1}-{end_offset} of {total_results})"
            )
            try:
                await context.bot.send_message(
                    text=monitoring_message_text,
                    chat_id=MONITORING_GROUP_ID
                )
            except Exception as e:
                print(f"Warning: Could not send monitoring message: {e}")
                
    except Exception as e:
        logger.error(f"Error in load_more_profiles_callback: {e}")
        await query.edit_message_text("Error loading more profiles. Please try again.")


async def send_profile_message_direct(chat_id: int, context: ContextTypes.DEFAULT_TYPE, profile):
    """Send profile message directly to chat_id (for pagination)"""
    profile_id = profile['id']
    
    # Use enhanced service to get formatted profile card
    formatted_profile = enhanced_profile_service.get_profile_card(profile_id)
    
    if not formatted_profile:
        # Fallback to basic message if service fails
        await context.bot.send_message(
            chat_id=chat_id,
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
                chat_id,
                formatted_profile.message_text,
                reply_markup,
                context
            )
        else:
            # Send as text message if image can't be displayed
            await context.bot.send_message(
                chat_id=chat_id,
                text=formatted_profile.message_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
    else:
        # Send as text message (no media)
        await context.bot.send_message(
            chat_id=chat_id,
            text=formatted_profile.message_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )


async def expand_profile_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Enhanced expand profile callback using service layer"""
    query = update.callback_query
    await query.answer()

    try:
        # Check if this is a back button callback
        if query.data.startswith('back_to_card_'):
            profile_id = query.data.split('_')[3].strip()
            logger.info(f"Back to card requested for profile ID: '{profile_id}' from callback data: '{query.data}'")
            
            # Use enhanced service to get card format
            formatted_profile = enhanced_profile_service.get_profile_card(profile_id)
            
            if not formatted_profile:
                await query.edit_message_text(f"Profile not found. (ID: {profile_id})")
                return
            
            # Get the reply markup from formatted profile
            reply_markup = formatted_profile.get_inline_keyboard_markup()
            
            # Update message back to card format
            if message_contains_media(query.message):
                await query.edit_message_caption(
                    caption=formatted_profile.message_text,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
            else:
                await query.edit_message_text(
                    text=formatted_profile.message_text,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
            return

        # Handle product detail callbacks
        if query.data.startswith('product_detail_'):
            product_id = query.data.split('_')[2].strip()
            logger.info(f"Product detail requested for product ID: '{product_id}'")
            await handle_product_detail(query, product_id)
            return

        # Handle asset detail callbacks
        if query.data.startswith('asset_detail_'):
            asset_id = query.data.split('_')[2].strip()
            logger.info(f"Asset detail requested for asset ID: '{asset_id}'")
            await handle_asset_detail(query, asset_id)
            return

        # Handle more products callback
        if query.data.startswith('more_products_'):
            profile_id = query.data.split('_')[2].strip()
            logger.info(f"More products requested for profile ID: '{profile_id}'")
            await handle_more_products(query, profile_id)
            return

        # Handle more assets callback
        if query.data.startswith('more_assets_'):
            profile_id = query.data.split('_')[2].strip()
            logger.info(f"More assets requested for profile ID: '{profile_id}'")
            await handle_more_assets(query, profile_id)
            return

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

async def handle_product_detail(query, product_id: str):
    """Handle product detail callback using API"""
    try:
        product_data = api.get_product_detail(product_id)
        
        if not product_data:
            await query.edit_message_text("Product details not available.")
            return
        
        # Escape markdown characters to prevent parsing errors
        def escape_markdown(text):
            if not text:
                return text
            # Escape problematic characters
            for char in ['_', '*', '[', ']', '`', '\\']:
                text = text.replace(char, f'\\{char}')
            return text
        
        # Format product information with escaped text
        message_parts = [
            f"*🔧 Product Details*",
            f"*Name:* {escape_markdown(product_data.get('name', 'Unknown'))}",
            f"*Type:* {escape_markdown(product_data.get('productType', {}).get('name', '-'))}",
            f"*Status:* {escape_markdown(product_data.get('productStatus', {}).get('name', '-'))}",
        ]
        
        if product_data.get('description'):
            message_parts.append(f"*Description:* {escape_markdown(product_data['description'])}")
        
        if product_data.get('launchDate'):
            message_parts.append(f"*Launch Date:* {escape_markdown(product_data['launchDate'])}")
        
        # Add asset relationships if available
        if product_data.get('productAssetRelationships'):
            assets = [rel.get('asset', {}).get('name') for rel in product_data['productAssetRelationships']
                     if rel.get('asset', {}).get('name')]
            if assets:
                escaped_assets = [escape_markdown(asset) for asset in assets[:3]]
                message_parts.append(f"*Related Assets:* {', '.join(escaped_assets)}")
        
        # Create buttons for URLs and back button
        buttons = []
        
        # Add URL buttons if available with null safety
        product_urls = product_data.get('urls', []) or []
        if product_urls:
            for url_obj in product_urls[:3]:  # Limit to 3 URLs
                if url_obj and url_obj.get('url'):
                    url_type = url_obj.get('urlType', {}).get('name', 'Link')
                    # Create appropriate button text based on URL type
                    if 'website' in url_type.lower():
                        button_text = "🌐 Website"
                    elif 'documentation' in url_type.lower() or 'docs' in url_type.lower():
                        button_text = "📚 Docs"
                    elif 'whitepaper' in url_type.lower():
                        button_text = "📄 Whitepaper"
                    elif 'blog' in url_type.lower():
                        button_text = "📝 Blog"
                    else:
                        button_text = f"🔗 {url_type}"
                    
                    buttons.append([InlineKeyboardButton(button_text, url=url_obj['url'])])
        
        # Get the profile ID from the product's root relationship
        profile_id = "unknown"
        if product_data.get('root', {}).get('id'):
            profile_id = product_data['root']['id']
        elif product_data.get('rootId'):
            profile_id = product_data['rootId']
        
        # Add back button
        buttons.append([InlineKeyboardButton("← Back", callback_data=f"back_to_card_{profile_id}")])
        reply_markup = InlineKeyboardMarkup(buttons)
        
        await query.edit_message_text(
            text="\n".join(message_parts),
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Error handling product detail for ID {product_id}: {e}")
        await query.edit_message_text("Error loading product details.")


async def handle_asset_detail(query, asset_id: str):
    """Handle asset detail callback using API"""
    try:
        asset_data = api.get_asset_detail(asset_id)
        
        if not asset_data:
            await query.edit_message_text("Asset details not available.")
            return
        
        # Escape markdown characters to prevent parsing errors
        def escape_markdown(text):
            if not text:
                return text
            # Escape problematic characters
            for char in ['_', '*', '[', ']', '`', '\\']:
                text = text.replace(char, f'\\{char}')
            return text
        
        # Format asset information with escaped text
        message_parts = [
            f"*💎 Asset Details*",
            f"*Name:* {escape_markdown(asset_data.get('name', 'Unknown'))}",
            f"*Ticker:* {escape_markdown(asset_data.get('ticker', '-'))}",
            f"*Type:* {escape_markdown(asset_data.get('assetType', {}).get('name', '-'))}",
            f"*Status:* {escape_markdown(asset_data.get('assetStatus', {}).get('name', '-'))}",
        ]
        
        if asset_data.get('description'):
            message_parts.append(f"*Description:* {escape_markdown(asset_data['description'])}")
        
        # Create buttons for URLs and back button
        buttons = []
        
        # Add URL buttons if available with null safety
        asset_urls = asset_data.get('urls', []) or []
        if asset_urls:
            for url_obj in asset_urls[:3]:  # Limit to 3 URLs
                if url_obj and url_obj.get('url'):
                    url_type = url_obj.get('urlType', {}).get('name', 'Link')
                    # Create appropriate button text based on URL type
                    if 'website' in url_type.lower():
                        button_text = "🌐 Website"
                    elif 'documentation' in url_type.lower() or 'docs' in url_type.lower():
                        button_text = "📚 Docs"
                    elif 'whitepaper' in url_type.lower():
                        button_text = "📄 Whitepaper"
                    elif 'explorer' in url_type.lower() or 'scan' in url_type.lower():
                        button_text = "🔍 Explorer"
                    elif 'social' in url_type.lower() or 'twitter' in url_type.lower():
                        button_text = "🐦 Social"
                    else:
                        button_text = f"🔗 {url_type}"
                    
                    buttons.append([InlineKeyboardButton(button_text, url=url_obj['url'])])
        
        # Get the profile ID from the asset's root relationship
        profile_id = "unknown"
        if asset_data.get('root', {}).get('id'):
            profile_id = asset_data['root']['id']
        elif asset_data.get('rootId'):
            profile_id = asset_data['rootId']
        
        # Add back button
        buttons.append([InlineKeyboardButton("← Back", callback_data=f"back_to_card_{profile_id}")])
        reply_markup = InlineKeyboardMarkup(buttons)
        
        await query.edit_message_text(
            text="\n".join(message_parts),
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Error handling asset detail for ID {asset_id}: {e}")
        await query.edit_message_text("Error loading asset details.")


async def handle_more_products(query, profile_id: str):
    """Handle more products callback"""
    try:
        # Get profile data to show all products
        profile_data = enhanced_profile_service.get_raw_profile_data(profile_id, full_data=True)
        
        if not profile_data or not profile_data.products:
            await query.edit_message_text("No additional products found.")
            return
        
        valid_products = [p for p in profile_data.products if p.name and p.name != 'Unknown']
        
        message_parts = [
            f"*🔧 All Products for {profile_data.name}*",
            ""
        ]
        
        # List all products
        for i, product in enumerate(valid_products, 1):
            message_parts.append(f"{i}. *{product.name}*")
            if hasattr(product, 'product_type') and product.product_type:
                message_parts.append(f"   Type: {product.product_type.name}")
            message_parts.append("")
        
        # Create back button
        buttons = [[InlineKeyboardButton("← Back to Profile", callback_data=f"back_to_card_{profile_id}")]]
        reply_markup = InlineKeyboardMarkup(buttons)
        
        await query.edit_message_text(
            text="\n".join(message_parts),
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Error handling more products for profile ID {profile_id}: {e}")
        await query.edit_message_text("Error loading products.")


async def handle_more_assets(query, profile_id: str):
    """Handle more assets callback"""
    try:
        # Get profile data to show all assets
        profile_data = enhanced_profile_service.get_raw_profile_data(profile_id, full_data=True)
        
        if not profile_data or not profile_data.assets:
            await query.edit_message_text("No additional assets found.")
            return
        
        valid_assets = [a for a in profile_data.assets if a.name and a.name != 'Unknown']
        
        message_parts = [
            f"*💎 All Assets for {profile_data.name}*",
            ""
        ]
        
        # List all assets
        for i, asset in enumerate(valid_assets, 1):
            message_parts.append(f"{i}. *{asset.name}*")
            if hasattr(asset, 'ticker') and asset.ticker:
                message_parts.append(f"   Ticker: {asset.ticker}")
            if hasattr(asset, 'asset_type') and asset.asset_type:
                message_parts.append(f"   Type: {asset.asset_type.name}")
            message_parts.append("")
        
        # Create back button
        buttons = [[InlineKeyboardButton("← Back to Profile", callback_data=f"back_to_card_{profile_id}")]]
        reply_markup = InlineKeyboardMarkup(buttons)
        
        await query.edit_message_text(
            text="\n".join(message_parts),
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Error handling more assets for profile ID {profile_id}: {e}")
        await query.edit_message_text("Error loading assets.")


def message_contains_media(message):
    # print("message", message)
    # print("message photo", message.photo)
    return bool(message.photo)

