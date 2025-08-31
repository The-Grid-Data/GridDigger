from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler

import api
from handlers import FILTER_MAIN, FILTER_SUB, FILTER_CHOICES, FILTER_FILLING, utils
from api import get_profiles
from handlers.utils import show_profiles, generate_applied_filters_text, create_main_menu_filter_keyboard


async def show_filters_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    user_data = context.user_data
    user_data.setdefault("FILTERS", {})
    user_data.setdefault("inc_search", False)
    results = api.get_profiles(user_data)
    results_count = len(results) if results is not None else 0

    keyboard = create_main_menu_filter_keyboard(user_data, results_count)
    
    # Enhanced message with better UX
    total_profiles = api.get_total_profile_count()
    filter_text = generate_applied_filters_text(user_data)
    
    if filter_text and filter_text != "No filters applied":
        message = f"🔍 **Profile Search Results**\n\n**Applied filters:**\n{filter_text}\n\n**Found results:** {results_count:,} of {total_profiles:,} total profiles"
    else:
        message = f"🔍 **Profile Search & Filter**\n\n📊 **{total_profiles:,} profiles** available to search\n\n**Current filters:** None\n**Found results:** {results_count:,}"

    await query.edit_message_text(message, reply_markup=keyboard, parse_mode='Markdown')
    return FILTER_MAIN


async def handle_filter_main_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    data = context.user_data
    data.setdefault("FILTERS", {})
    data.setdefault("inc_search", False)

    data["FILTERS"]["profileNameSearch"] = update.message.text
    data["FILTERS"]["profileNameSearch_query"] = update.message.text

    # todo apply filters here

    results = get_profiles(data)
    results_count = len(results) if results is not None else 0

    keyboard = create_main_menu_filter_keyboard(data, results_count)
    
    # Enhanced message for text search
    total_profiles = api.get_total_profile_count()
    search_term = update.message.text
    search_mode = "Deep Search" if data.get('inc_search', False) else "Quick Search"
    
    message = f"🔍 **Search Results**\n\n"
    message += f"**Search term:** \"{search_term}\"\n"
    message += f"**Search mode:** {search_mode}\n"
    message += f"**Found results:** {results_count:,} of {total_profiles:,} total profiles\n\n"
    message += f"💡 *Tip: Use the toggle button below to switch between Quick (names only) and Deep (names + descriptions) search modes*"

    await update.message.reply_text(message, reply_markup=keyboard, parse_mode='Markdown')
    return FILTER_MAIN


async def start_over_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.edit_message_text(f"This menu has expired, start over please. /filters")
    return ConversationHandler.END


async def handle_filter_sub_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    data = context.user_data

    if query.data == "back_to_main_filters":
        return await show_filters_main_menu(update, context)
    elif query.data.startswith("show"):  # could be more precise
        return await show_profiles(data, update, context)
    elif query.data.startswith('reset'):
        if utils.reset_filters(data):
            return await show_sub_filters(update, context)
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Already reset")
            return FILTER_SUB
    query_data = query.data.split("_", 1)
    filter_type = query_data[0]
    sub_filter = query_data[1]

    print("query_data", query_data)
    print("filter_type", filter_type)
    print("sub_filter", sub_filter)

    # Fetch sub-filters dynamically based on filter_type
    sub_filters = api.get_sub_filters(filter_type)

    print("sub_filters", sub_filters)

    # Determine the filter type (searchable or multiple)
    filter_meta = next((f for f in sub_filters if f['query'] == sub_filter), None)
    if not filter_meta:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Something wrong happened")
        return await show_filters_main_menu(update, context)

    print("filter label", filter_meta['label'])
    filter_type = filter_meta['type']
    data['current_filter'] = {}
    data['current_filter'] = sub_filter
    data['current_filter_type'] = {}
    data['current_filter_type'] = filter_type


    print("filter_meta['type'] (filter_type)", filter_type)
    print("data['current_filter'] (sub_filter)", sub_filter)

    if filter_type == 'searchable':
        message = f"✏️ **Enter Search Value**\n\n"
        message += f"**Filter:** {filter_meta['label']}\n"
        message += f"**Type:** Text search\n\n"
        message += f"💡 *Type your search term and press Enter*"
        
        await query.edit_message_text(message, parse_mode='Markdown')
        return FILTER_FILLING
    elif filter_type == 'multiple':
        filter_query = api.filters_config["filters_queries"].get(filter_meta['query'])
        filter_options = api.fetch_filter_options(filter_query)

        buttons = [
            [InlineKeyboardButton(option['name'], callback_data=f"{sub_filter}_{option['id']}")]
            for option in filter_options
        ]
        buttons.append([InlineKeyboardButton("Back", callback_data="back_to_sub_main_filters")])
        reply_markup = InlineKeyboardMarkup(buttons)

        message = f"📋 **Select Option**\n\n"
        message += f"**Filter:** {filter_meta['label']}\n"
        message += f"**Available options:** {len(filter_options)}\n\n"
        message += f"💡 *Choose one of the options below*"
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        return FILTER_CHOICES


async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    data = context.user_data
    current_filter = data.get('current_filter')

    if current_filter:
        data[current_filter] = user_input
        await update.message.reply_text(f"Value '{user_input}' saved for {current_filter}.")
        return FILTER_MAIN
    else:
        await update.message.reply_text("No active filter.")
        return FILTER_MAIN


async def handle_choice_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    data = context.user_data

    sub_filter, choice_id = query.data.split("_")
    data[sub_filter] = choice_id

    await query.edit_message_text(f"Option '{choice_id}' saved for {sub_filter}.")
    return FILTER_MAIN


async def handle_filter_choices_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    data = context.user_data

    if query.data == "back_to_sub_main_filters":
        return await show_sub_filters(update, context)
    else:
        filter_sub_type, id = query.data.rsplit('_', 1)
        print("filter_sub_type", filter_sub_type)
        print("id", id)
        data.setdefault("FILTERS", {})
        data["FILTERS"][filter_sub_type + '_query'] = id
        # api request to get value via id
        button_text = next(
            button.text for row in update.callback_query.message.reply_markup.inline_keyboard for button in row if
            button.callback_data == query.data)

        data["FILTERS"][filter_sub_type] = button_text  # for printing filter data on menu
        print("button_text", button_text)
        # store filter name in data as well
        return await show_sub_filters(update, context)


async def handle_filter_filling_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    data = context.user_data

    data["FILTERS"][data["current_filter"]] = update.message.text
    data["FILTERS"][data["current_filter"]+'_query'] = update.message.text
    await update.message.reply_text(f"Value '{update.message.text}' saved for {data['current_filter']}.")

    filter_type = data.setdefault('filter_type', 'None')

    data.setdefault("FILTERS", {})
    for key, value in data["FILTERS"].items():
        print(f"Key: {key}, Value: {value}")
    if filter_type == "None":

        return await show_filters_main_menu(update, context) # it'll show an error if reached here
    else:

        profiles = api.get_profiles(data)
        profile_count = len(profiles) if profiles is not None else 0
        display_results_count = min(profile_count, 20)

        # Fetch sub-filters dynamically based on filter_type
        sub_filters = api.get_sub_filters(filter_type)

        # Extract labels from sub_filters and create buttons
        buttons = [
            [InlineKeyboardButton(f"{'🟡' if data['FILTERS'].get(sub_filter['query']) else '🟢'}{sub_filter['label']}", callback_data=f"{filter_type}_{sub_filter['query']}")]
            for sub_filter in sub_filters]

        # Add "Show profiles" button if profile_count > 0
        if profile_count > 0:
            buttons.insert(0, [InlineKeyboardButton("Reset", callback_data=f"reset_{filter_type}_filters"),
                               InlineKeyboardButton(f"Show profiles ({display_results_count})",
                                                    callback_data=f"show_{filter_type}_filters")])
        else:
            buttons.insert(0, [InlineKeyboardButton("Reset", callback_data=f"reset_{filter_type}_filters")])

        buttons.append([InlineKeyboardButton("Back", callback_data="back_to_main_filters")])
        reply_markup = InlineKeyboardMarkup(buttons)

        # Enhanced message for filter results
        total_profiles = api.get_total_profile_count()
        filter_text = generate_applied_filters_text(data)
        
        message = f"✅ **Filter Applied**\n\n"
        message += f"**Applied filters:**\n{filter_text}\n\n"
        message += f"**Found results:** {profile_count:,} of {total_profiles:,} total profiles"
        
        await context.bot.send_message(chat_id=update.message.chat_id,
                                       text=message,
                                       reply_markup=reply_markup,
                                       parse_mode='Markdown')
        return FILTER_SUB


async def show_sub_filters(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    data = context.user_data
    filter_type = data.setdefault('filter_type', 'None')

    data.setdefault("FILTERS", {})
    for key, value in data["FILTERS"].items():
        print(f"Key: {key}, Value: {value}")
    if filter_type == "None":

        return await show_filters_main_menu(update, context)
    else:

        profiles = api.get_profiles(data)
        profile_count = len(profiles) if profiles is not None else 0

        # Fetch sub-filters dynamically based on filter_type
        sub_filters = api.get_sub_filters(filter_type)

        filters = data.get('FILTERS', {})
        profile_filter_emoji = "🟡" if 'profileNameSearch' in filters or 'profileType' in filters or 'profileSector' in filters or 'profileStatuses' in filters else '🟢'

        # Extract labels from sub_filters and create buttons
        buttons = [[InlineKeyboardButton(f"{'🟡' if data['FILTERS'].get(sub_filter['query']) else '🟢'}{sub_filter['label']}",
                                         callback_data=f"{filter_type}_{sub_filter['query']}")]
                   for sub_filter in sub_filters]
        buttons.insert(0, [InlineKeyboardButton("Reset", callback_data=f"reset_{filter_type}_filters"),
                           InlineKeyboardButton(f"Show profiles ({profile_count})",
                                                callback_data=f"show_{filter_type}_filters")])
        buttons.append([InlineKeyboardButton("Back", callback_data="back_to_main_filters")])
        reply_markup = InlineKeyboardMarkup(buttons)
        # Enhanced sub-filter menu message
        total_profiles = api.get_total_profile_count()
        filter_text = generate_applied_filters_text(data)
        
        message = f"🔧 **Advanced Filters**\n\n"
        if filter_text and filter_text != "No filters applied":
            message += f"**Applied filters:**\n{filter_text}\n\n"
        message += f"**Found results:** {profile_count:,} of {total_profiles:,} total profiles\n\n"
        message += f"💡 *Select a filter below to refine your search*"
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        return FILTER_SUB


