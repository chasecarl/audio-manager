import os
import queue
import subprocess
from collections import deque

from telegram.ext import *

from model import RawTextAudioCollection
from util import default_audio_name
from deniqq import deniqq


TELEGRAM_TOKEN_VARNAME = 'TGTOKEN'
TOKEN = os.environ.get(TELEGRAM_TOKEN_VARNAME)


class AudioQueueEntry(list):

    def __init__(self, query):
        super().__init__(query)
        self.name = default_audio_name(query)
        self.model = get_model()

    def ready(self):
        return all(name in self.model.keys() for name in self)

    def not_available(self):
        return [name for name in self if name not in self.model.keys()]


class AudioQueue():

    def __init__(self, model, bot, chat_id):
        self.model = model
        self.bot = bot
        self.chat_id = chat_id
        self.queue = deque()

    def add(self, query_entry):
        entry = AudioQueueEntry(query_entry)
        if not self._check_and_update_entry(entry):
            self.queue.append(entry)

    def _check_and_update_entry(self, entry):
        if entry.ready():
            self.upload_audio(entry)
            return True
        self.notify_not_available(entry)
        return False

    def update(self):
        for entry in self.queue:
            if self._check_and_update_entry(entry):
                self.queue.remove(entry)
                self.bot.send_message(
                    chat_id=self.chat_id,
                    text=f'The {entry.name} was updated'
                )
            self.notify_not_available(entry)

    def notify_not_available(self, entry):
        names = entry.not_available()
        joined_names_str = '\n'.join(names)
        msg = f'The following audio are missing for {entry.name}:\n{joined_names_str}'
        self.bot.send_message(
            chat_id=self.chat_id,
            text=msg
        )

    def upload_audio(self, entry):
        self.model.select(entry)
        audio_name = default_audio_name(entry)
        audio_path = f'./res/{audio_name}.m4a'
        model.concat_audio(audio_path)
        self.bot.send_message(
            chat_id=self.chat_id,
            text=f'Uploading {audio_name}...'
        )
        with open(audio_path, 'rb') as audio_fd:
            self.bot.send_document(
                chat_id=self.chat_id,
                document=audio_fd
            )


model = None
queue = None


def get_model():
    global model
    if not model:
        model = RawTextAudioCollection()
        model.load()
    return model


def get_queue(bot, chat_id):
    global queue
    if not queue:
        queue = AudioQueue(get_model(), bot, chat_id)
    return queue


def handle_audio_query(update, context):
    raw_query = update.message.text
    query = [deniqq(entry_name.strip()) for entry_name in raw_query.split('\n') if entry_name.strip()]
    queue = get_queue(context.bot, update.effective_chat.id)
    queue.add(query)
    # no need to update because the only query that can be available is the above one
    # and it's checked and the queue is updated when adding


def add_audio(update, context):
    audio = update.message.audio
    file = context.bot.get_file(audio.file_id)
    if not audio.title:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='I can\'t see the title of the audio. '
                 'Please use modified Audio Recorder that sets audio title.'
        )
    else:
        audio_path = f'./res/{audio.title}.flac'
        converted_audio_path = f'{audio_path[:-5]}.m4a'
        file.download(audio_path)
        subprocess.run(['ffmpeg', '-y', '-i', audio_path, '-acodec', 'alac', converted_audio_path])
        os.remove(audio_path)
        model = get_model()
        model.add(audio.title, converted_audio_path)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'Successfully added {audio.title}!'
        )
        get_queue(context.bot, update.effective_chat.id).update()


if __name__ == "__main__":
    updater = Updater(token=TOKEN)
    dispatcher = updater.dispatcher
    audio_query_handler = MessageHandler(Filters.text & (~Filters.command), handle_audio_query)
    add_audio_handler = MessageHandler(Filters.audio, add_audio)
    dispatcher.add_handler(audio_query_handler)
    dispatcher.add_handler(add_audio_handler)
    updater.start_polling()
    updater.idle()
    dispatcher.remove_handler(audio_query_handler)
