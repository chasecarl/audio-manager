import os
import logging

from typing import Iterable


ENV_DEBUG_VARNAME = 'AMDEBUG'
ENV_LOGGING_LEVEL_VARNAME = 'LOGLEVEL'


logging_level = os.environ.get(ENV_LOGGING_LEVEL_VARNAME)
if not logging_level:
    logging.basicConfig(level=logging.INFO)
else:
    logging.basicConfig(level=logging.DEBUG)


def debugging():
    result = os.environ.get(ENV_DEBUG_VARNAME) is not None
    if result:
        logging.debug(f'Debug check: {result}.')
    return result


def basename_without_ext(filepath):
    return os.path.splitext(os.path.basename(filepath))[0]


def default_audio_name(entries_names):
    return ','.join(entries_names)

def wrap_iterable(iterable_or_single_entry):
    if not isinstance(iterable_or_single_entry, Iterable) or isinstance(iterable_or_single_entry, str):
        return [iterable_or_single_entry]
    return iterable_or_single_entry
