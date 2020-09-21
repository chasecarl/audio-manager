import os
import logging


ENTRY_EXT = '.amf'


class EntryModel:

    def __init__(self, entry_path):
        self._entry_path = entry_path
        with open(self._entry_path) as entry_fd:
            self.name = next(entry_fd)
            self.audio_path = next(entry_fd)


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


    def set_selected(self, selection):
        self.selected = [entry for entry in self if entry.name in selection]
        logging.debug(f'M: Current selection is: {self._str_selected()}.')


    def _str_selected(self):
        return '[' + ', '.join(str(entry) for entry in self.selected) + ']'
