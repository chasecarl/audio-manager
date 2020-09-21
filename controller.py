import numpy as np
import tkinter as tk
import logging


from view import MainView
from model import ListModel
from util import *


def join(iterable, on):
    # assuming all the inputs have the same number of channels (shape[1])
    it = iter(iterable)
    # asssuming there is at least one object in the iterable
    joined_iterable = [next(it)]
    for el in it:
        joined_iterable.append(on)
        joined_iterable.append(el)
    return np.concatenate(joined_iterable, axis=0)


class Controller:

    def __init__(self, root):
        self.model = ListModel()
        self.view = MainView(root)
        self.model.add_callback(self.model_changed)
        self.view.add_callback(self.selection_changed)
        self.view.display_samples(self.model)
        self.view.add_button.config(command=self.add_entry)
        self.view.remove_button.config(command=self.remove_entry)
        self.view.rename_button.config(command=self.rename_entry)
        self.view.concat_button.config(command=self.concat_audio)


    def selection_changed(self, **kwargs):
        selection = kwargs[SELECTION]
        logging.debug(f'C: Passing the following selection to the model: {str(selection)}')
        self.model.set_selected(selection)


    def entry_added(self, **kwargs):
        name = kwargs[ENTRY_NAME]
        path = kwargs[ENTRY_PATH]
        self.view.remove_callback(self.entry_added)
        logging.debug(f'C: Passing the following entry to the model: {name}, {path}')
        self.model.add_entry(name, path)


    def entry_renamed(self, **kwargs):
        name = kwargs[ENTRY_NAME]
        self.view.remove_callback(self.entry_renamed)
        logging.debug(f'C: Passing the following entry name to the model: {name}')
        self.model.rename_entry(name)


    def audio_saved(self, **kwargs):
        audio_filename = kwargs[AUDIO_FILENAME]
        self.view.remove_callback(self.audio_saved)
        logging.debug(f'C: Passing the following audio filename to the model: {audio_filename}')
        self.model.concat_audio(audio_filename)


    def model_changed(self):
        self.view.display_samples(self.model)


    def add_entry(self):
        self.view.add_callback(self.entry_added)
        self.view.add_entry_dialog()


    def remove_entry(self):
        self.model.remove_entry()


    def rename_entry(self):
        self.view.add_callback(self.entry_renamed)
        self.view.rename_entry_dialog()


    def concat_audio(self):
        self.view.add_callback(self.audio_saved)
        self.view.save_concat_audio_dialog()


if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()
    app = Controller(root)
    root.mainloop()
