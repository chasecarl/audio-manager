import os

from telegram.ext import Updater, MessageHandler, Filters


TELEGRAM_TOKEN_VARNAME = 'TGTOKEN'
TOKEN = os.environ.get(TELEGRAM_TOKEN_VARNAME)


def handle_audio_query(update, context):
    raw_query = update.message.text
    query = raw_query.split('\n')
    for entry_name in query:
        context.bot.send_message(chat_id=update.effective_chat.id, text=entry_name)


if __name__ == "__main__":
    updater = Updater(token=TOKEN)
    dispatcher = updater.dispatcher
    audio_query_handler = MessageHandler(Filters.text & (~Filters.command), handle_audio_query)
    dispatcher.add_handler(audio_query_handler)
    updater.start_polling()
    updater.idle()
    dispatcher.remove_handler(audio_query_handler)
