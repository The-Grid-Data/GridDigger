from telegram import Update
from telegram.ext import ConversationHandler, CommandHandler, filters, MessageHandler, CallbackQueryHandler
import re

from handlers import FILTER_MAIN, FILTER_SUB, FILTER_CHOICES, FILTER_FILLING
from handlers.commands import start, help_command, filter
from handlers.profiles import handle_filter_main_callback, expand_profile_callback
from handlers.filters import handle_filter_main_text, handle_filter_sub_callback, handle_filter_choices_callback, \
    handle_filter_filling_text


def setup(application):
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("filter", filter),
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_filter_main_text),
        ]
        ,
        states={
            FILTER_MAIN: [CallbackQueryHandler(handle_filter_main_callback)],
            FILTER_SUB: [CallbackQueryHandler(handle_filter_sub_callback)],
            FILTER_CHOICES: [CallbackQueryHandler(handle_filter_choices_callback)],
            FILTER_FILLING: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_filter_filling_text)],
        },
        fallbacks=[
            CommandHandler("filter", filter),
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_filter_main_text),
            #CallbackQueryHandler(query_result_handler),
        ],
        per_message=False,
    )
    application.add_handler(CommandHandler("start", start))
    #application.add_handler(CommandHandler("show_filters", filter))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(conv_handler)  # for flows

    application.add_handler(CallbackQueryHandler(expand_profile_callback, pattern=r'^expand_'))

    #application.run_polling(allowed_updates=Update.ALL_TYPES, poll_interval=0)
