import os


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
