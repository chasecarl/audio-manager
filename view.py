import tkinter as tk
from util import debugging


TITLE = 'Audio Manager'
LABEL_TEXT = 'My Database'


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

        self.sample_list = tk.Listbox(self.top_frame, selectmode='extended')
        self.sample_list.pack(side='top', anchor='w')

        self.bot_frame = tk.Frame(self)
        self.bot_frame.pack(side='bottom', expand=True, fill='both')
        if debugging():
            self.bot_frame.config(bg='blue')


    def display_samples(self, samples):
        self.sample_list.delete(0, tk.END)
        for sample in samples:
            self.sample_list.insert(tk.END, sample)
