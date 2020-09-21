import tkinter as tk
import logging


from util import debugging


TITLE = 'Audio Manager'
LABEL_TEXT = 'My Database'
ADD_TEXT = 'Add'
REMOVE_TEXT = 'Remove'
RENAME_TEXT = 'Rename'
PLAY_TEXT = 'Play'
CONCAT_TEXT = 'Merge Audio'


class MainView(tk.Toplevel):

    def __init__(self, master):
        tk.Toplevel.__init__(self, master)
        self.protocol('WM_DELETE_WINDOW', self.master.destroy)
        self.title(TITLE)

        self.callbacks = []

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


    def _from_indices(self, indices):
        return [self.sample_list.get(i) for i in indices]


    def _do_callbacks(self):
        for func in self.callbacks:
            func(self._from_indices(self.sample_list.curselection()))


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
