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
            command=self._add_entry
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


    def _add_entry(self):
        if self.name_entry.get() == '' or self.path_entry.get() == '':
            logging.debug(f'M: The name or the path were empty. Nothing was added.')
            return
        self.master._add_entry(self.name_entry.get(), self.path_entry.get())
        logging.debug(f'M: The entry was added successfully.')
        self.grab_release()
        self.destroy()


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
            command=self._rename_entry
        )
        self.accept_button.pack(side='left')


    def _rename_entry(self):
        if self.name_entry.get() == '':
            logging.debug(f'M: The name was empty. Nothing was added.')
            return
        self.master._rename_entry(self.name_entry.get())
        logging.debug(f'M: The entry was renamed successfully.')
        self.grab_release()
        self.destroy()


class MainView(tk.Toplevel):

    def __init__(self, master):
        tk.Toplevel.__init__(self, master)
        self.protocol('WM_DELETE_WINDOW', self.master.destroy)
        self.title(TITLE)

        self.callbacks = []
        self.entry_name = None
        self.new_entry_path = None
        self.audio_filename = None

        self.top_frame = tk.Frame(self)
        self.top_frame.pack(side='top', expand=True, fill='both')
        if debugging():
            self.top_frame.config(bg='red')

        self.label = tk.Label(self.top_frame, text=LABEL_TEXT)
        self.label.pack(side='top', anchor='w')

        self.top_left = tk.Frame(self.top_frame)
        self.top_left.pack(side='left', expand=True, fill='both')

        self.sample_list = tk.Listbox(self.top_left, selectmode='extended')
        self.sample_list.bind('<<ListboxSelect>>', lambda e: self._listbox_select_handler())
        self.sample_list.pack(side='top', anchor='w')

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


    def display_samples(self, samples):
        self.sample_list.delete(0, tk.END)
        for sample in samples:
            self.sample_list.insert(tk.END, sample)
        self._do_callbacks()


    def add_callback(self, func):
        self.callbacks.append(func)


    def remove_callback(self, func):
        self.callbacks.remove(func)


    def _from_indices(self, indices):
        return [self.sample_list.get(i) for i in indices]


    def _do_callbacks(self):
        data = {
            SELECTION: self._from_indices(self.sample_list.curselection()),
            ENTRY_NAME: self.entry_name,
            ENTRY_PATH: self.new_entry_path,
            AUDIO_FILENAME: self.audio_filename
        }
        for func in self.callbacks:
            func(**data)


    def _listbox_select_handler(self):
        self._do_callbacks()
        selection_size = len(self.sample_list.curselection())
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


    def add_entry_dialog(self):
        dialog = AddView(self)
        dialog.grab_set()


    def rename_entry_dialog(self):
        dialog = RenameView(self)
        dialog.grab_set()


    def _add_entry(self, name, path):
        self.entry_name = name
        self.new_entry_path = path
        self._do_callbacks()


    def _rename_entry(self, name):
        self.entry_name = name
        self._do_callbacks()


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
            self._do_callbacks()
