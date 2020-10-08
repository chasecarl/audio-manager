import tkinter as tk
from tkinter import messagebox
import logging


from view import *
from model import RawTextAudioCollection
from util import *


class Controller:

    def __init__(self, root):
        self.model = RawTextAudioCollection()
        self.view = MainView(root)
        self.model.add_callback(self.model_changed)
        self.view.display(self.model)
        self.view.add_button.config(command=self.dialog_add_entry)
        self.view.remove_button.config(command=self.dialog_remove_entry)
        self.view.rename_button.config(command=self.dialog_rename_entry)
        self.view.concat_button.config(command=self.dialog_concat_audio)
        self.current_dialog = None

    def model_changed(self):
        self.view.display(self.model)

    def _dispose_current_dialog(self):
        if not self.current_dialog:
            return
        self.current_dialog.destroy()
        self.current_dialog = None

    def dialog_add_entry(self):
        self.current_dialog = AddView(self.view)
        self.current_dialog.accept_button.config(command=self.add_entry)
        self.current_dialog.grab_set()

    def add_entry(self):
        # TODO validate
        self.model.add((self.current_dialog.name_entry.get(), ), (self.current_dialog.path_entry.get(), ))
        self._dispose_current_dialog()

    def dialog_remove_entry(self):
        answer = messagebox.askokcancel(
            title='Confirm removal',
            message='Are you sure to remove selected items?',
            icon='warning'
        )
        if answer:
            self.remove_entries()

    def remove_entries(self):
        # TODO validate
        selection = self.model.names_selected()
        self.model.remove(selection)

    def dialog_rename_entry(self):
        self.current_dialog = RenameView(self.view)
        self.current_dialog.accept_button.config(command=self.rename_entry)
        self.current_dialog.grab_set()

    def rename_entry(self):
        # TODO validate
        selection = self.model.names_selected()
        self.model.rename(selection[0], self.current_dialog.name_entry.get())
        self._dispose_current_dialog()

    def dialog_concat_audio(self):
        self.view.save_concat_audio_dialog()


if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()
    app = Controller(root)
    root.mainloop()
