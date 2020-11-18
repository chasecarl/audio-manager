import os
from os import path
from typing import Iterable, Union
from types import new_class
from pathlib import Path
from enum import Enum, auto
from ctypes import c_uint16 as mutable_int
from ctypes import c_bool as mutable_bool

from model import RawTextAudioCollection as Model
from util import basename_without_ext as bwe
from util import default_audio_name as dan
from util import wrap_iterable
from deniqq import deniqq


AUDIO_DIR = 'res'

LOOP_DIALOG = 'loop_dialog_key'
CHOICE_MSG = 'choice_msg_key'

MutableInt = new_class('MutableInt', bases=(mutable_int, ))
MutableBool = new_class('MutableBool', bases=(mutable_bool, ))


class Choice(Enum):
    YES = auto()
    NO = auto()
    QUIT = auto()
    ONE_MORE = auto()
    ONE_LESS = auto()

    def one_letter(self):
        unq_start_letter_name = self.name.split('_')
        unq_start_letter_name = unq_start_letter_name[len(unq_start_letter_name) - 1]
        return unq_start_letter_name[0].lower()

    def __str__(self):
        return self.name.lower().replace('_', ' ')

    @classmethod
    def describe_choices(cls, choices=[], exclude=[]):
        choices = wrap_iterable(choices)
        exclude = wrap_iterable(exclude)
        choices = choices if choices else cls
        if choices and exclude:
            print('Ignoring exclude...')
            exclude = []
        return ', '.join(f'{c.one_letter()} for {str(c)}' for c in choices if c not in exclude)

    @classmethod
    def from_letter(cls, letter, choices=[], exclude=[]):
        choices = wrap_iterable(choices)
        exclude = wrap_iterable(exclude)
        choices = choices if choices else cls
        if choices and exclude:
            print('Ignoring exclude...')
            exclude = []
        for c in choices:
            if c in exclude:
                continue
            if c.one_letter() == letter:
                return c
        else:
            raise ValueError('Invalid choice!')

    @classmethod
    def interactive_from_letter(cls, msg='Choose one', choices=[], exclude=[]):
        if choices and exclude:
            print('Ignoring exclude...')
            exclude = []
        return Choice.from_letter(
            input(f'{msg} ({cls.describe_choices(choices=choices, exclude=exclude)}): '),
            choices=choices,
            exclude=exclude
        )


def interactive_get_int() -> int:
    while True:
        try:
            return int(input('Enter the number of entries: ',))
        except ValueError:
            print('Enter a valid integer!')
            continue

def dialog(terminated: MutableBool, handlers={}) -> None:
    if not handlers:
        handlers[Choice.QUIT] = lambda: terminated.__setattr__('value', True)
    choices = list(filter(lambda key: isinstance(key, Choice), handlers.keys()))
    while not terminated:
        if LOOP_DIALOG in handlers.keys():
            handlers[LOOP_DIALOG]()
        try:
            choice = Choice.interactive_from_letter(
                msg=handlers[CHOICE_MSG],
                choices=choices,
            )
            handlers[choice]()
        except ValueError as e:
            print(f'{str(e)} Try again!')
            continue

def interactive_confirm_paths(paths: Iterable[Union[Path, str]], n_recent: MutableInt) -> Iterable[str]:
    dialog_terminated = mutable_bool(False)
    recent_paths = []
    handlers = {
        LOOP_DIALOG: lambda: (recent_paths.__init__(list(map(str, paths[-n_recent.value:]))), print(f'Here are the paths chosen:\n{recent_paths}')),
        CHOICE_MSG: 'Confirm your choice',
        Choice.YES: lambda: dialog_terminated.__setattr__('value', True),
        Choice.ONE_LESS: lambda: n_recent.__setattr__('value', n_recent.value - 1),
        Choice.ONE_MORE: lambda: n_recent.__setattr__('value', n_recent.value + 1),
        Choice.QUIT: lambda: (recent_paths.__imul__(0), dialog_terminated.__setattr__('value', True))
    }
    dialog(dialog_terminated, handlers=handlers)
    return recent_paths

def interactive_get_paths_to_add() -> Iterable[str]:
    n_recent = mutable_int(interactive_get_int())
    paths = sorted(Path('res').iterdir(), key=os.path.getmtime)
    return interactive_confirm_paths(paths, n_recent)

def interactive_from_gdrive_table_clipboard() -> Iterable[str]:
    print('Copy words from the Google Drive table you want audio with and paste them here:')
    names = []
    first_line = True
    while True:
        name = input()
        if first_line:
            first_line = False
            continue
        if not name:
            break
        names.append(deniqq(name).strip())
    return names 

def audio_path_from_names(names: Iterable[str]) -> str:
    return os.path.join(AUDIO_DIR, f'{dan(names)}.m4a')

def interactive_process_audio_query(model: Model) -> None:
    names = interactive_from_gdrive_table_clipboard()
    audio_path = audio_path_from_names(names)
    model.select(names)
    # TODO confirm names selected
    print('Writing the audio...')
    model.concat_audio(audio_path)
    print('Audio was written successfully!')
    model.deselect(names)

def prepare(model) -> None:
    paths_to_add = interactive_get_paths_to_add()
    if paths_to_add:
        names_to_add = list(map(bwe, paths_to_add))
        model.add(names_to_add, paths_to_add)  # TODO make add async?

def interactive_process_audio_query_loop(model) -> None:
    interactive_process_audio_query(model)
    dialog_terminated = mutable_bool(False)
    handlers = {
        CHOICE_MSG: 'Do you want to make more audios?',
        Choice.YES: lambda: interactive_process_audio_query(model),
        Choice.NO: lambda: dialog_terminated.__setattr__('value', True),
    }
    dialog(dialog_terminated, handlers=handlers)


def mainloop() -> None:
    model = Model()  # TODO make load async
    prepare(model)
    interactive_process_audio_query_loop(model)


if __name__ == '__main__':
    mainloop()
