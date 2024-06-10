from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

import api
from api import get_profiles


async def profile_result_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    data = context.user_data
    results = get_profiles(data)

    if query.data == "more": # for now
        await query.edit_message_text("Showing profiles", )
        for profile in results:
            pass #await send_profile_message(update, context, profile)
        return ConversationHandler.END
    return ConversationHandler.END


# this function should accept a json data of profile. Eg: [{"name": "Bitcoin", "id": 1}
# Your job here is to request profile data from the API according to its id
# name, id, sector, main product type, issued Assets, Tag line, short description, icon or logo link, URL, docs, twitter (social if any)
# and send a message to the user of profile data shown in attached screenshot
