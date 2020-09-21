import os
import logging


ENV_DEBUG_VARNAME = 'AMDEBUG'


logging.basicConfig(level=logging.DEBUG)


def debugging():
    result = os.environ.get(ENV_DEBUG_VARNAME) is not None
    if result:
        logging.debug(f'Debug check: {result}.')
    return result
