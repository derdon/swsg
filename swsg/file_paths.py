from os import getenv, path

XDG_DATA_HOME = getenv(
    'XDG_DATA_HOME', path.expanduser(path.join('~', '.local', 'share')))
PROJECT_DATA_DIR = path.join(XDG_DATA_HOME, 'swsg')
LOGFILE = path.join(PROJECT_DATA_DIR, 'swsg.log')
DEFAULT_PROJECTS_FILE_NAME = os.path.join(PROJECT_DATA_DIR, 'projects.shelve')
