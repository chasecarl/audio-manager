import os
import logging
import abc
from typing import Tuple, Iterable
from collections import deque

from pydub import AudioSegment


ENTRY_EXT = '.amf'

ENTRIES_FOLDER_PATH = 'res'

PAUSE_SECS = 2


class AudioEntry(metaclass=abc.ABCMeta):

    """An interface that represents an audio entry."""

    @classmethod
    def __subclasshook__(cls, subclass) -> bool:
        return (hasattr(subclass, 'save')
                and (
                    callable(subclass.save)
                    or NotImplemented
                )
                and hasattr(subclass, 'load_audio')
                and (
                    callable(subclass.load_audio)
                    or NotImplemented
                )
                and hasattr(subclass, 'set_name')
                and (
                    callable(subclass.set_name)
                    or NotImplemented
                ))

    @abc.abstractmethod
    def save(self) -> None:
        """Saves the entry to the disk."""
        raise NotImplementedError

    @abc.abstractmethod
    def load_audio(self) -> Tuple[AudioSegment, int]:
        """Loads audio of the entry."""
        raise NotImplementedError

    @abc.abstractmethod
    def set_name(self, name: str) -> None:
        """Sets the name of the entry and saves it."""
        raise NotImplementedError

    @abc.abstractmethod
    def get_name(self) -> str:
        """Returns the name of the entry."""
        raise NotImplementedError


class RawTextAudioEntry(AudioEntry):

    """An audio entry that is stored in a raw text file."""
    # TODO the strange thing is that it if the file is not in the default directory it will be created

    def __init__(self, name, audio_path, dir=ENTRIES_FOLDER_PATH):
        self.dir = dir
        self._entry_path = None
        self.name = name
        self.audio_path = audio_path

    def save(self) -> None:
        if not self._entry_path:
            self._entry_path = os.path.join(self.dir, f'{self.name}{ENTRY_EXT}')
        with open(self._entry_path, 'w', encoding='utf8') as entry_fd:
            entry_fd.writelines((
                f'{self.name}\n',
                self.audio_path
            ))
            entry_fd.truncate()

    def set_name(self, name: str) -> None:
        self.name = name
        self.save()

    def get_name(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name

    def load_audio(self) -> Tuple[AudioSegment, int]:
        audio = AudioSegment.from_file(self.audio_path)
        return audio, audio.frame_rate


class AudioCollection(dict, metaclass=abc.ABCMeta):

    """A collection of audio entries."""

    def __init__(self):
        dict.__init__(self)
        self.load()
        self._names_selected = deque()

    @abc.abstractmethod
    def add(self, names: Iterable[str], audio_paths: Iterable[str]) -> None:
        """Adds entries to the collection."""
        raise NotImplementedError

    @abc.abstractmethod
    def remove(self, names: Iterable[str]) -> None:
        """Removes entries from the collection."""
        raise NotImplementedError

    @abc.abstractmethod
    def rename(self, name: str, new_name: str) -> None:
        """Renames an entry."""
        raise NotImplementedError

    @abc.abstractmethod
    def load(self) -> None:
        """Loads all the entries."""
        raise NotImplementedError

    def _str_selected(self) -> str:
        return '[' + ', '.join(str(entry) for entry in self._names_selected) + ']'

    def select(self, names: Iterable[str]) -> None:
        """Adds names to the selection."""
        for name in names:
            if name not in self.keys():
                logging.error(f'M: Trying to select an item that isn\'t a part of the collection: {name}')
                continue
            self._names_selected.append(name)
        logging.debug(f'M: Current selection is: {self._str_selected()}.')

    def deselect(self, names: Iterable[str]) -> None:
        """Removes names from the selection."""
        for name in names:
            if name not in self.keys():
                logging.error(f'M: Trying to deselect an item that isn\'t a part of the collection: {name}')
                continue
            try:
                self._names_selected.remove(name)
            except ValueError:
                logging.error(f'M: Trying to deselect an item that isn\'t selected: {name}')
        logging.debug(f'M: Current selection is: {self._str_selected()}.')

    def concat_audio(self, audio_filename):
        if len(self._names_selected) < 2:
            logging.error(f'M: Audio concatenation function is called with less than two entries selected. Aborting.')
            return
        on = AudioSegment.silent(PAUSE_SECS * 1000)
        result, sr = self[self._names_selected[0]].load_audio()
        for sample_name in self._names_selected[1:]:
            audio, sample_sr = self[sample_name].load_audio()
            if sample_sr != sr:
                logging.warning(f'M: Audio samples have different sampling rate, writing with the first encountered one.')
            result += on
            result += audio
        result.export(audio_filename, format='wav')
        logging.debug(f'M: Concatenated audio was written successfully!')


class RawTextAudioCollection(AudioCollection):

    """An audio collection that uses entries stored in raw text files."""

    def add(self, names: Iterable[str], audio_paths: Iterable[str]) -> None:
        for name, audio_path in zip(names, audio_paths):
            if name in self.keys():
                continue
            entry = RawTextAudioEntry(name, audio_path)
            self[name] = entry
            entry.save()

    def remove(self, names: Iterable[str]) -> None:
        for name in names:
            # TODO logging.error for consistency with deselect?
            self.pop(name, None)  # doesn't throw an exception if there is no such entry
        self.deselect(names)

    def rename(self, name: str, new_name: str) -> None:
        entry = self[name]
        entry.set_name(new_name)
        try:
            i = self._names_selected.index(name)
            self._names_selected.insert(i, new_name)
            self._names_selected.remove(name)
        except ValueError:
            logging.error(f'M: Item isn\'t selected when renaming: {name}')

    def load(self, dir=ENTRIES_FOLDER_PATH) -> None:
        for entry_path in os.listdir(dir):
            if entry_path.endswith(ENTRY_EXT):
                with open(entry_path, encoding='utf8') as entry_fd:
                    name = next(entry_fd).strip()
                    audio_path = next(entry_fd).strip()
                entry = RawTextAudioEntry(name, audio_path)
                self[entry.get_name()] = entry
