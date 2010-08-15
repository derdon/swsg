from logbook import Logger
from logbook.base import NOTICE

__version__ = '0.1a'
swsg_logger = Logger('SWSG Logger', level=NOTICE)
XDG_DATA_HOME = os.getenv(
    'XDG_DATA_HOME', os.path.expanduser(os.path.join('~', '.local', 'share')))
PROJECT_DATA_DIR = os.path.join(XDG_DATA_HOME, 'swsg')
