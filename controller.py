import tkinter as tk
from tkinter import messagebox, filedialog
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
        self.view.entries_listbox.bind('<<ListboxSelect>>', lambda e: self._listbox_select_handler())
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
        self.model.add(self.current_dialog.name_entry.get(), self.current_dialog.path_entry.get())
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
        filepath = filedialog.asksaveasfilename(
            title=CONCAT_TITLE,
            filetypes=(
                ('m4a Files', '*.m4a'),
                ('All Files', '*.*'),
            ),
            defaultextension='.m4a',
            initialdir='./res/',
            initialfile=default_audio_name(self.model.names_selected())
        )
        if filepath:
            self.model.concat_audio(filepath)

    def _listbox_select_handler(self):
        view_selection = self.view.selection()
        logging.debug(f'C: View selection before listbox handler: {view_selection}')
        model_selection = list(self.model.names_selected())
        logging.debug(f'C: Model selection before listbox handler: {model_selection}')
        for view_entry in view_selection:
            if view_entry not in model_selection:
                self.model.select((view_entry, ))
        for model_entry in model_selection:
            if model_entry not in view_selection:
                self.model.deselect((model_entry, ))
        logging.debug(f'C: View selection after listbox handler: {list(self.view.selection())}')
        logging.debug(f'C: Model selection after listbox handler: {list(self.model.names_selected())}')
        self.view.listbox_select_handler()


if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()
    app = Controller(root)
    root.mainloop()
