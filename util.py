import os
import logging


ENV_DEBUG_VARNAME = 'AMDEBUG'
ENV_LOGGING_LEVEL_VARNAME = 'LOGLEVEL'


SELECTION = 'selection'
ENTRY_NAME = 'name'
ENTRY_PATH = 'path'
AUDIO_FILENAME = 'audio'


logging_level = os.environ.get(ENV_LOGGING_LEVEL_VARNAME)
if not logging_level:
    logging.basicConfig(level=logging.INFO)
else:
    logging.basicConfig(level=logging.DEBUG)
logging.getLogger('numba.core.ssa').setLevel(logging.ERROR)
logging.getLogger('numba.core.byteflow').setLevel(logging.ERROR)
logging.getLogger('numba.core.interpreter').setLevel(logging.ERROR)


def debugging():
    result = os.environ.get(ENV_DEBUG_VARNAME) is not None
    if result:
        logging.debug(f'Debug check: {result}.')
    return result
