import os
import logging


ENV_DEBUG_VARNAME = 'AMDEBUG'


logging.basicConfig(level=logging.INFO)


def debugging():
    result = os.environ.get(ENV_DEBUG_VARNAME) is not None
    if result:
        logging.info(f'Debug check: {result}.')
    return result
