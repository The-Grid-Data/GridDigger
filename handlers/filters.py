from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler

import api
from handlers import FILTER_MAIN, FILTER_SUB, FILTER_CHOICES, FILTER_FILLING, utils
from api import get_profiles
from handlers.utils import show_profiles, generate_applied_filters_text


def show_filters_main_menu(update: Update, context) -> int:
    query = update.callback_query
    user_data = context.user_data
    user_data.setdefault("FILTERS", {})
    user_data['FILTERS'].setdefault("inc_search", False)

    results_count = len(api.get_profiles(user_data))  # Assuming get_profiles function takes user_data and returns results

    # Limit the number of results shown on the button text to 20
    display_results_count = min(results_count, 20)

    filters = user_data.get('FILTERS', {})
    profile_filter_emoji = "🟡" if 'profileNameSearch' in filters or 'profileType' in filters or 'profileSector' in filters or 'profileStatuses' in filters else '🟢'
    product_filter_emoji = "🟡" if 'productTypes' in filters or 'productStatuses' in filters else '🟢'
    entity_filter_emoji = "🟡" if 'entityTypes' in filters or 'entityName' in filters else '🟢'
    asset_filter_emoji = "🟡" if 'assetTickers' in filters or 'assetTypes' in filters or 'assetStandards' in filters else '🟢'

    # Create buttons
    keyboard_buttons = [
        [InlineKeyboardButton(f'{profile_filter_emoji}Profile filters', callback_data='profile_filters'),
         InlineKeyboardButton(f'{product_filter_emoji}Product filters', callback_data='product_filters')],
        [InlineKeyboardButton(f'{asset_filter_emoji}Asset filters', callback_data='asset_filters'),
         InlineKeyboardButton(f'{entity_filter_emoji}Entity filters', callback_data='entity_filters')],
        [InlineKeyboardButton('🔄Reset Filters', callback_data='reset_all'),
         InlineKeyboardButton(f"{'✔️' if user_data['FILTERS']['inc_search'] else ''}Inc search", callback_data='inc_search')]
    ]

    # Add "Show profiles" button if results_count > 0
    if results_count > 0:
        keyboard_buttons.insert(0, [InlineKeyboardButton(f'Show profiles ({display_results_count})', callback_data='show')])

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    query.edit_message_text(f"Applied filters:\n{generate_applied_filters_text(user_data)}\nFound results: {results_count}", reply_markup=keyboard)
    return FILTER_MAIN


def handle_filter_main_text(update: Update, context) -> int:
    data = context.user_data
    data.setdefault("FILTERS", {})
    data['FILTERS'].setdefault("inc_search", False)

    data["FILTERS"]["profileNameSearch"] = update.message.text
    data["FILTERS"]["profileNameSearch_query"] = update.message.text

    # todo apply filters here

    results = get_profiles(data)
    results_count = len(results)

    # Limit the number of results shown on the button text to 20
    display_results_count = min(results_count, 20)

    filters = data.get('FILTERS', {})
    profile_filter_emoji = "🟡" if 'profileNameSearch' in filters or 'profileType' in filters or 'profileSector' in filters or 'profileStatuses' in filters else '🟢'
    product_filter_emoji = "🟡" if 'productTypes' in filters or 'productStatuses' in filters else '🟢'
    entity_filter_emoji = "🟡" if 'entityTypes' in filters or 'entityName' in filters else '🟢'
    asset_filter_emoji = "🟡" if 'assetTickers' in filters or 'assetTypes' in filters or 'assetStandards' in filters else '🟢'

    # Create buttons
    keyboard_buttons = [
        [InlineKeyboardButton(f'{profile_filter_emoji}Profile filters', callback_data='profile_filters'),
         InlineKeyboardButton(f'{product_filter_emoji}Product filters', callback_data='product_filters')],
        [InlineKeyboardButton(f'{asset_filter_emoji}Asset filters', callback_data='asset_filters'),
         InlineKeyboardButton(f'{entity_filter_emoji}Entity filters', callback_data='entity_filters')],
        [InlineKeyboardButton('🔄Reset Filters', callback_data='reset_all'),
         InlineKeyboardButton(f"{'✔️' if data['FILTERS']['inc_search'] else ''}Inc search", callback_data='inc_search')]
    ]

    # Add "Show profiles" button if results_count > 0
    if results_count > 0:
        keyboard_buttons.insert(0, [InlineKeyboardButton(f'Show profiles ({display_results_count})', callback_data='show')])

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

    update.message.reply_text(f"Applied filters: {generate_applied_filters_text(data)}\nFound results: {results_count}", reply_markup=keyboard)
    return FILTER_MAIN


def start_over_handler(update: Update, context) -> int:
    query = update.callback_query
    query.edit_message_text(f"This menu has expired, start over please. /filters")
    return ConversationHandler.END


def handle_filter_sub_callback(update: Update, context) -> int:
    query = update.callback_query
    query.answer()

    data = context.user_data

    if query.data == "back_to_main_filters":
        return show_filters_main_menu(update, context)
    elif query.data.startswith("show"):  # could be more precise
        return show_profiles(data, update, context)
    elif query.data.startswith('reset'):
        if utils.reset_filters(data):
            return show_sub_filters(update, context)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Already reset")
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
        context.bot.send_message(chat_id=update.effective_chat.id, text="Something wrong happened")
        return show_filters_main_menu(update, context)

    print("filter label", filter_meta['label'])
    filter_type = filter_meta['type']
    data['current_filter'] = {}
    data['current_filter'] = sub_filter
    data['current_filter_type'] = {}
    data['current_filter_type'] = filter_type


    print("filter_meta['type'] (filter_type)", filter_type)
    print("data['current_filter'] (sub_filter)", sub_filter)

    if filter_type == 'searchable':
        query.edit_message_text(f"Enter the value for {filter_meta['label']}:")
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

        query.edit_message_text(f"Choose an option for {filter_meta['label']}:", reply_markup=reply_markup)
        return FILTER_CHOICES


def handle_text_input(update: Update, context) -> int:
    user_input = update.message.text
    data = context.user_data
    current_filter = data.get('current_filter')

    if current_filter:
        data[current_filter] = user_input
        update.message.reply_text(f"Value '{user_input}' saved for {current_filter}.")
        return FILTER_MAIN
    else:
        update.message.reply_text("No active filter.")
        return FILTER_MAIN


def handle_choice_selection(update: Update, context) -> int:
    query = update.callback_query
    query.answer()
    data = context.user_data

    sub_filter, choice_id = query.data.split("_")
    data[sub_filter] = choice_id

    query.edit_message_text(f"Option '{choice_id}' saved for {sub_filter}.")
    return FILTER_MAIN


def handle_filter_choices_callback(update: Update, context) -> int:
    query = update.callback_query
    query.answer()

    data = context.user_data

    if query.data == "back_to_sub_main_filters":
        return show_sub_filters(update, context)
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
        return show_sub_filters(update, context)


def handle_filter_filling_text(update: Update, context) -> int:
    data = context.user_data

    data["FILTERS"][data["current_filter"]] = update.message.text
    data["FILTERS"][data["current_filter"]+'_query'] = update.message.text
    update.message.reply_text(f"Value '{update.message.text}' saved for {data['current_filter']}.")

    filter_type = data.setdefault('filter_type', 'None')

    data.setdefault("FILTERS", {})
    for key, value in data["FILTERS"].items():
        print(f"Key: {key}, Value: {value}")
    if filter_type == "None":

        return show_filters_main_menu(update, context) # it'll show an error if reached here
    else:

        profiles = api.get_profiles(data)
        profile_count = len(profiles)
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

        context.bot.send_message(chat_id=update.message.chat_id,
                                       text=f"Applied filters: {generate_applied_filters_text(data)}\nFound results: {profile_count}",
                                       reply_markup=reply_markup)
        return FILTER_SUB


def show_sub_filters(update: Update, context) -> int:
    query = update.callback_query
    query.answer()
    data = context.user_data
    filter_type = data.setdefault('filter_type', 'None')

    data.setdefault("FILTERS", {})
    for key, value in data["FILTERS"].items():
        print(f"Key: {key}, Value: {value}")
    if filter_type == "None":

        return show_filters_main_menu(update, context)
    else:

        profiles = api.get_profiles(data)
        profile_count = len(profiles)

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
        query.edit_message_text(f"Applied filters:\n{generate_applied_filters_text(data)}", reply_markup=reply_markup)
        return FILTER_SUB


