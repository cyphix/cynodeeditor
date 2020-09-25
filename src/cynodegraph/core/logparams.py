# pylint: disable=missing-module-docstring
# pylint: disable=no-name-in-module
from __future__ import generator_stop
from __future__ import annotations

"""Quick and easy config for logging module.
"""
import logging, sys, os



file_log_formatter = logging.Formatter('[t:%(asctime)s][pid:%(process)d][%(levelname)s][mod: %(module)s][func: %(funcName)s][line: %(lineno)d] >> %(message)s')
console_log_formatter = logging.Formatter('[pid:%(process)d][%(levelname)s][mod: %(module)s][func: %(funcName)s][line: %(lineno)d] >> %(message)s')

file_path = 'temp/'
# check if directory exist
if not os.path.exists('temp'):
    os.makedirs('temp')



def logging_config(to_console=True, to_file=True, console_level=logging.DEBUG, file_level=logging.DEBUG, file_destination = 'debug.log'):
    if(to_file):
        # create the file logger
        logging.basicConfig(filename=file_path+file_destination, filemode='w', level=logging.DEBUG, format='[t:%(asctime)s][pid:%(process)d][%(levelname)s][mod: %(module)s][func: %(funcName)s][line: %(lineno)d] >> %(message)s')

        if(to_console):
            # create the console logger
            console_log = logging.StreamHandler()
            console_log.setLevel(console_level)
            console_log.setFormatter(console_log_formatter)
            # add the handler to the root logger
            logging.getLogger('').addHandler(console_log)
    else:
        logging.basicConfig(stream=sys.stderr, level=logging.ERROR, format='[pid:%(process)d][%(levelname)s][mod: %(module)s][func: %(funcName)s][line: %(lineno)d] >> %(message)s')

def change_level(level, dest='console'):
    # TODO: !!! DOESNT WORK
    if(dest == 'console'):
        logging.getLogger('console_log').setLevel(level)
