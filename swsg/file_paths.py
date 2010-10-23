from os import getenv, path

XDG_DATA_HOME = getenv(
    'XDG_DATA_HOME', path.expanduser(path.join('~', '.local', 'share')))
XDG_CONFIG_HOME = getenv(
    'XDG_CONFIG_HOME', path.expanduser(path.join('~', '.config')))
GLOBAL_CONFIGFILE = path.join(XDG_CONFIG_HOME, 'swsg')
PROJECT_DATA_DIR = path.join(XDG_DATA_HOME, 'swsg')
LOGFILE = path.join(PROJECT_DATA_DIR, 'swsg.log')
DEFAULT_PROJECTS_FILE_NAME = path.join(PROJECT_DATA_DIR, 'projects.shelve')
