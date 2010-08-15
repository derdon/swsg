from os import getenv, path

from logbook import Logger
from logbook.base import NOTICE

__version__ = '0.1a'
XDG_DATA_HOME = getenv(
    'XDG_DATA_HOME', path.expanduser(path.join('~', '.local', 'share')))
PROJECT_DATA_DIR = path.join(XDG_DATA_HOME, 'swsg')
swsg_logger = Logger('SWSG Logger', level=NOTICE)
LOGFILE = path.join(PROJECT_DATA_DIR, 'swsg.log')
