import os
import logging


ENTRY_EXT = '.amf'

ENTRIES_FOLDER_PATH = 'res'


class EntryModel:

    def __init__(self, entry_path):
        self._entry_path = entry_path
        with open(self._entry_path) as entry_fd:
            self.name = next(entry_fd).strip()
            self.audio_path = next(entry_fd).strip()


    @classmethod
    def write(cls, name, audio_path):
        entry_path = os.path.join(ENTRIES_FOLDER_PATH, f'{name}{ENTRY_EXT}')
        with open(entry_path, 'w') as entry_fd:
            entry_fd.writelines((
                f'{name}\n',
                audio_path
            ))
        return cls(entry_path)


    def set_name(self, name):
        self.name = name
        with open(self._entry_path, 'w') as entry_fd:
            entry_fd.writelines((
                f'{self.name}\n',
                self.audio_path
            ))
            entry_fd.truncate()


    def __str__(self):
        return self.name


class ListModel(list):

    def __init__(self):
        list.__init__(self)
        for entry_path in os.listdir(ENTRIES_FOLDER_PATH):
            if entry_path.endswith(ENTRY_EXT):
                self.append(EntryModel(os.path.join(ENTRIES_FOLDER_PATH, entry_path)))
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


    def add_entry(self, name, path):
        new_entry = EntryModel.write(name, path)
        self.append(new_entry)
        self._do_callbacks()


    def remove_entry(self):
        if len(self.selected) == 0:
            logging.error(f'M: Remove is called with an empty selection. Not removing.')
            return
        for to_remove in self.selected:
            self.remove(to_remove)
            os.remove(to_remove._entry_path)
        self._do_callbacks()


    def rename_entry(self, name):
        if len(self.selected) == 0:
            logging.error(f'M: Rename is called with an empty selection. Not removing.')
            return
        if len(self.selected) > 1:
            logging.error(f'M: Rename is called with more than one entry selected. Not renaming.')
            return
        to_rename = self.selected[0]
        to_rename.set_name(name)
        self._do_callbacks()
