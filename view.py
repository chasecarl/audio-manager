import tkinter as tk
from tkinter import filedialog
import logging


from util import *


TITLE = 'Audio Manager'
LABEL_TEXT = 'My Database'
ADD_TEXT = 'Add'
REMOVE_TEXT = 'Remove'
RENAME_TEXT = 'Rename'
PLAY_TEXT = 'Play'
CONCAT_TEXT = 'Merge Audio'
ADD_TITLE = 'Add Entry'
RENAME_TITLE = 'Rename Entry'
PATH_ENTRY_TITLE = 'Choose an audio file...'
CONCAT_TITLE = CONCAT_TEXT
ENTRY_NAME_TEXT = 'Name:'
NEW_ENTRY_NAME_TEXT = 'New name:'
ENTRY_PATH_TEXT = 'Audio file path:'
BROWSE_BUTTON_TEXT = '...'
ACCEPT_BUTTON_TEXT = 'OK'


class AddView(tk.Toplevel):

    def __init__(self, master):
        tk.Toplevel.__init__(self, master)
        self.master = master
        self.title(ADD_TITLE)

        self.name_frame = tk.Frame(self)
        self.name_frame.pack(side='top', expand=True, fill='both')

        self.name_label = tk.Label(self.name_frame, text=ENTRY_NAME_TEXT)
        self.name_label.pack(side='left')

        self.name_entry = tk.Entry(self.name_frame)
        self.name_entry.pack(side='left')

        self.path_frame = tk.Frame(self)
        self.path_frame.pack(side='top', expand=True, fill='both')

        self.path_label = tk.Label(self.path_frame, text=ENTRY_PATH_TEXT)
        self.path_label.pack(side='left')

        self.path_entry_text_var = tk.StringVar(self.path_frame)
        self.path_entry = tk.Entry(self.path_frame, text=self.path_entry_text_var)
        self.path_entry.pack(side='left')

        self.path_browse_button = tk.Button(
            self.path_frame,
            text=BROWSE_BUTTON_TEXT,
            command=self._update_path_entry
        )
        self.path_browse_button.pack(side='left')

        self.accept_frame = tk.Frame(self)
        self.accept_frame.pack(side='bottom', expand=True, fill='both')

        self.accept_button = tk.Button(
            self.accept_frame,
            text=ACCEPT_BUTTON_TEXT,
        )
        self.accept_button.pack(side='left')

    def _update_path_entry(self):
        path = filedialog.askopenfilename(
            title=PATH_ENTRY_TITLE,
            filetypes=(
                ('MPEG-4 Audio Files', '*.m4a'),
                ('WAV Files', '*.wav'),
                ('All Files', '*.*'),
            ),
            defaultextension='.m4a',
            initialdir='./res/'
        )
        self.path_entry_text_var.set(path)


class RenameView(tk.Toplevel):

    def __init__(self, master):

        tk.Toplevel.__init__(self, master)
        self.master = master
        self.title(RENAME_TITLE)

        self.name_frame = tk.Frame(self)
        self.name_frame.pack(side='top', expand=True, fill='both')

        self.name_label = tk.Label(self.name_frame, text=NEW_ENTRY_NAME_TEXT)
        self.name_label.pack(side='left')

        self.name_entry = tk.Entry(self.name_frame)
        self.name_entry.pack(side='left')

        self.accept_frame = tk.Frame(self)
        self.accept_frame.pack(side='bottom', expand=True, fill='both')

        self.accept_button = tk.Button(
            self.accept_frame,
            text=ACCEPT_BUTTON_TEXT,
        )
        self.accept_button.pack(side='left')


class MainView(tk.Toplevel):

    def __init__(self, master):
        tk.Toplevel.__init__(self, master)
        self.protocol('WM_DELETE_WINDOW', self.master.destroy)
        self.title(TITLE)

        self.top_frame = tk.Frame(self)
        self.top_frame.pack(side='top', expand=True, fill='both')
        if debugging():
            self.top_frame.config(bg='red')

        self.label = tk.Label(self.top_frame, text=LABEL_TEXT)
        self.label.pack(side='top', anchor='w')

        self.top_left = tk.Frame(self.top_frame)
        self.top_left.pack(side='left', expand=True, fill='both')

        self.entries_listbox = tk.Listbox(self.top_left, selectmode='extended')
        self.entries_listbox.pack(side='top', anchor='w')

        self.top_right = tk.Frame(self.top_frame)
        self.top_right.pack(side='right', expand=True, fill='both')

        self.add_button = tk.Button(self.top_right, text=ADD_TEXT)
        self.add_button.pack(side='top', anchor='center')

        self.remove_button = tk.Button(self.top_right, text=REMOVE_TEXT, state=tk.DISABLED)
        self.remove_button.pack(side='top', anchor='center')

        self.rename_button = tk.Button(self.top_right, text=RENAME_TEXT, state=tk.DISABLED)
        self.rename_button.pack(side='top', anchor='center')

        self.bot_frame = tk.Frame(self)
        self.bot_frame.pack(side='bottom', expand=True, fill='both')
        if debugging():
            self.bot_frame.config(bg='blue')

        self.play_button = tk.Button(self.bot_frame, state=tk.DISABLED, text=PLAY_TEXT)
        self.play_button.pack(side='left')

        self.concat_button = tk.Button(self.bot_frame, state=tk.DISABLED, text=CONCAT_TEXT)
        self.concat_button.pack(side='left')

    def display(self, entries):
        self.entries_listbox.delete(0, tk.END)
        for entry_name in entries.keys():
            self.entries_listbox.insert(tk.END, entry_name)

    def selection(self):
        return list(map(
            lambda i: self.entries_listbox.get(i),
            self.entries_listbox.curselection()
        ))

    def listbox_select_handler(self):
        selection_size = len(self.entries_listbox.curselection())
        logging.debug(f'V: Selection size is {selection_size}')
        # remove button logic
        if selection_size >= 1:
            self.remove_button.config(state=tk.NORMAL)
        else:
            self.remove_button.config(state=tk.DISABLED)
        # rename button logic
        if selection_size == 1:
            self.rename_button.config(state=tk.NORMAL)
        else:
            self.rename_button.config(state=tk.DISABLED)
        # play button logic
        if selection_size == 1:
            self.play_button.config(state=tk.NORMAL)
        else:
            self.play_button.config(state=tk.DISABLED)
        # cocnat button logic
        if selection_size > 1:
            self.concat_button.config(state=tk.NORMAL)
        else:
            self.concat_button.config(state=tk.DISABLED)

    def save_concat_audio_dialog(self):
        filename = filedialog.asksaveasfilename(
            title=CONCAT_TITLE,
            filetypes=(
                ('WAV Files', '*.wav'),
                ('All Files', '*.*'),
            ),
            defaultextension='.wav',
            initialdir='./res/'
        )
        if filename and filename != '':
            logging.debug(f'V: Passing the following audio filename to the controller: {filename}')
            self.audio_filename = filename
