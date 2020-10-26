import os
import logging


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
