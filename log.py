import tg


def log(tag, message):
    app = "GridDigger"
    tg.debug_telegram_bot(app, tag, message)
