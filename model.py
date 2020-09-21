import os
import logging


ENTRY_EXT = '.amf'


class EntryModel:

    def __init__(self, entry_path):
        self._entry_path = entry_path
        with open(self._entry_path) as entry_fd:
            self.name = next(entry_fd).strip()
            self.audio_path = next(entry_fd).strip()


    def set_name(self, name):
        self.name = name
        with open(self._entry_path, 'w') as entry_fd:
            entry_fd.writelines((
                self.name,
                self.audio_path
            ))
            entry_fd.truncate()


    def __str__(self):
        return self.name


class ListModel(list):

    ENTRIES_FOLDER_PATH = 'res'

    def __init__(self):
        list.__init__(self)
        for entry_path in os.listdir(ListModel.ENTRIES_FOLDER_PATH):
            if entry_path.endswith(ENTRY_EXT):
                self.append(EntryModel(os.path.join(ListModel.ENTRIES_FOLDER_PATH, entry_path)))
        self.selected = []
        self.callbacks = []


    def set_selected(self, selection):
        self.selected = [entry for entry in self if entry.name in selection]
        logging.debug(f'M: Current selection is: {self._str_selected()}.')


    def _str_selected(self):
        return '[' + ', '.join(str(entry) for entry in self.selected) + ']'


    def add_callback(self, func):
        self.callbacks.append(func)


    def _do_callbacks(self):
        for func in self.callbacks:
            func()


    def remove_entry(self):
        if len(self.selected) == 0:
            logging.error(f'M: Remove is called with an empty selection. Not removing.')
            return
        if len(self.selected) > 1:
            logging.warning(f'M: Remove is called with more than one entry selected. Removing the first one.')
        to_remove = self.selected[0]
        self.remove(to_remove)
        os.remove(to_remove._entry_path)
        self._do_callbacks()
