import os
import subprocess
import logging
import abc
from typing import Tuple, Iterable, Union
from collections import deque
from functools import wraps

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
                os.path.relpath(self.audio_path)
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


class EntryExists(Exception):
    def __init__(self, entry_name=None):
        msg = 'Entry with this name already exists' 
        if entry_name:
            msg += f': {entry_name}'
        msg += '!'
        super().__init__(msg)


class AudioCollection(dict, metaclass=abc.ABCMeta):

    """A collection of audio entries."""

    def __init__(self):
        dict.__init__(self)
        self._callbacks = []
        self.load()
        self._names_selected = deque()

    class Decorators:
        @classmethod
        def with_callbacks(cls, f):
            @wraps(f)
            def wrapper(*args, **kwds):
                f(*args, **kwds)
                logging.debug(f'M: Doing callbacks for {f.__name__}...')
                # args[0] is self
                args[0]._do_callbacks()
                logging.debug('M: Done.')
            return wrapper

    @Decorators.with_callbacks
    def add(self, names: Union[str, Iterable[str]], audio_paths: Union[str, Iterable[str]]) -> None:
        """Adds entries to the collection."""
        if type(names) == str:
            assert(type(audio_paths) == str)
            self._add(names, audio_paths)
        else:
            for entry in zip(names, audio_paths):
                self._add(*entry)

    @abc.abstractmethod
    def _add(self, name: str, audio_path: str) -> None:
        """Adds an entry to the collection."""
        raise NotImplementedError

    @Decorators.with_callbacks
    def remove(self, names: Union[str, Iterable[str]]) -> None:
        """Removes entries from the collection."""
        if type(names) == str:
            self._remove(names)
        else:
            for name in names:
                self._remove(name)
        self.deselect(names)

    @abc.abstractmethod
    def _remove(self, name: str) -> None:
        """Removes an entry from the collection."""
        raise NotImplementedError

    @Decorators.with_callbacks
    def rename(self, names: Union[str, Iterable[str]], new_names: Union[str, Iterable[str]]) -> None:
        """Renames entries in the collection."""
        if type(names) == str:
            assert(type(new_names) == str)
            self._rename(names, new_names)
        else:
            for entry in zip(names, new_names):
                self._rename(*entry)

    @abc.abstractmethod
    def _rename(self, name: str, new_name: str) -> None:
        """Renames an entry in the collection."""
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

    def deselect(self, names: Union[str, Iterable[str]]) -> None:
        """Removes names from the selection."""
        if type(names) == str:
            names = (names, )
        for name in names:
            if name not in self.keys():
                logging.error(f'M: Trying to deselect an item that isn\'t a part of the collection: {name}')
                continue
            try:
                self._names_selected.remove(name)
            except ValueError:
                logging.error(f'M: Trying to deselect an item that isn\'t selected: {name}')
        logging.debug(f'M: Current selection is: {self._str_selected()}.')

    def names_selected(self):
        """Returns the names of currently selected entries."""
        return self._names_selected

    def concat_audio(self, output_audio_filepath):
        if len(self._names_selected) < 2:
            logging.error(f'M: Audio concatenation function is called with less than two entries selected. Aborting.')
            return
        on = AudioSegment.silent(PAUSE_SECS * 1000)
        result, sr = self[self._names_selected[0]].load_audio()
        for sample_name in list(self._names_selected)[1:]:
            audio, sample_sr = self[sample_name].load_audio()
            if sample_sr != sr:
                logging.warning(f'M: Audio samples have different sampling rate, writing with the first encountered one.')
            result += on
            result += audio
        # we assume that the path contains extension of 3 letters
        wav_path = f'{output_audio_filepath[:-4]}.wav'
        result.export(wav_path, format='wav')
        subprocess.run(['ffmpeg', '-y', '-i', wav_path, output_audio_filepath], capture_output=True)
        os.remove(wav_path)
        logging.debug(f'M: Concatenated audio was written successfully!')

    def add_callback(self, func):
        """Adds a function that is called after every model update (excluding selection changes)."""
        self._callbacks.append(func)

    def _do_callbacks(self):
        """Performs all the callbacks."""
        for func in self._callbacks:
            func()


class RawTextAudioCollection(AudioCollection):

    """An audio collection that uses entries stored in raw text files."""

    def _add(self, name: str, audio_path: str) -> None:
        if name in self.keys():
            raise EntryExists(entry_name=name)
        entry = RawTextAudioEntry(name, audio_path)
        self[name] = entry
        entry.save()

    def _remove(self, name: str) -> None:
        # TODO logging.error for consistency with deselect?
        self.pop(name)  # doesn't throw an exception if there is no such entry

    def _rename(self, name: str, new_name: str) -> None:
        entry = self[name]
        entry.set_name(new_name)
        try:
            i = self._names_selected.index(name)
            self._names_selected.insert(i, new_name)
            self._names_selected.remove(name)
        except ValueError:
            logging.error(f'M: Item isn\'t selected when renaming: {name}')

    @AudioCollection.Decorators.with_callbacks
    def load(self, dir=ENTRIES_FOLDER_PATH) -> None:
        for entry_path in os.listdir(dir):
            if entry_path.endswith(ENTRY_EXT):
                with open(os.path.join(dir, entry_path), encoding='utf8') as entry_fd:
                    name = next(entry_fd).strip()
                    audio_path = next(entry_fd).strip()
                entry = RawTextAudioEntry(name, audio_path)
                self[entry.get_name()] = entry
