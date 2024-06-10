from telegram import Update
from telegram.ext import ConversationHandler, CommandHandler, filters, MessageHandler, CallbackQueryHandler
import re

import handlers
from handlers.commands import start, help_command
from handlers.profile_handler import query_result_handler, expand_profile_callback
from handlers.search_handler import search_profiles_handler, start_over_handler
from handlers.search_results_handler import profile_result_handler

SEARCH_READY, MAIN_FILTERS_MENU, SUB_FILTERS_MENU, TYPING, SEARCH_RESULTS = range(5)
END = ConversationHandler.END


def generate_pattern(current_state):
    # Define a pattern that excludes the current state
    return re.compile(f'^(?!{current_state}).*')


def setup(application):
    conv_handler = ConversationHandler(
        entry_points=[
            # CallbackQueryHandler(query_result_handler),
            MessageHandler(filters.TEXT & ~filters.COMMAND, search_profiles_handler),
            #CallbackQueryHandler(start_over_handler, pattern=generate_pattern(END))# how to set the pattern to all states except the current one?
        ]
        ,
        states={
            SEARCH_RESULTS: [CallbackQueryHandler(query_result_handler)],
            # ALL_FILTERS_MENU: [CallbackQueryHandler(filter_menu_handler)],
            # CHOOSING: [CallbackQueryHandler(choice_filter_handler)],
            # TYPING: [
            #     CallbackQueryHandler(typing_button_handler),
            #     MessageHandler(filters.TEXT & ~filters.COMMAND, typing_text_handler)
            # ],
        },
        fallbacks=[
            # CallbackQueryHandler(query_result_handler),
            MessageHandler(filters.TEXT & ~filters.COMMAND, search_profiles_handler),
            CallbackQueryHandler(query_result_handler)
        ],
        per_message=False,

        map_to_parent={
            END: END
        }
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(conv_handler)  # for flows

    application.add_handler(CallbackQueryHandler(profile_result_handler, pattern=re.compile(r'^more.*')))
    application.add_handler(CallbackQueryHandler(expand_profile_callback, pattern=r'^expand_'))

    application.run_polling(allowed_updates=Update.ALL_TYPES, poll_interval=0)
