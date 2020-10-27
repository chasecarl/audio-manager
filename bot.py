import os
import telegram

from telegram.ext import Updater, MessageHandler, Filters

from model import RawTextAudioCollection
from util import default_audio_name


TELEGRAM_TOKEN_VARNAME = 'TGTOKEN'
TOKEN = os.environ.get(TELEGRAM_TOKEN_VARNAME)

model = None


def handle_audio_query(update, context):
    raw_query = update.message.text
    query = [entry_name.strip() for entry_name in raw_query.split('\n')]
    global model
    if not model:
        model = RawTextAudioCollection()
        model.load()
    all_entries_in_db = True
    for entry_name in query:
        if entry_name in model.keys():
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f'The {entry_name} is found in the database!'
            )
        else:
            all_entries_in_db = False
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f'There is no {entry_name} in the database!'
            )
    if all_entries_in_db:
        model.select(query)
        audio_name = default_audio_name(query)
        audio_path = f'./res/{audio_name}.m4a'
        model.concat_audio(audio_path)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'Uploading the audio...'
        )
        with open(audio_path, 'rb') as audio_fd:
            context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=audio_fd
            )


if __name__ == "__main__":
    updater = Updater(token=TOKEN)
    dispatcher = updater.dispatcher
    audio_query_handler = MessageHandler(Filters.text & (~Filters.command), handle_audio_query)
    dispatcher.add_handler(audio_query_handler)
    updater.start_polling()
    updater.idle()
    dispatcher.remove_handler(audio_query_handler)
