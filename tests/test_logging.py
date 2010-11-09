import py
from logbook import FileHandler, INFO, DEBUG, ERROR
from swsg.file_paths import LOGFILE as DEFAULT_LOGFILE
from swsg.cli import get_logging_handler, set_logging_level

from utils import Object


@py.test.mark.skipif('os.name != "nt"')
def test_get_logging_handler_win():
    args = Object()
    args.logfile = None
    py.test.raises(OSError, 'get_logging_handler(args)')


@py.test.mark.skipif('os.name == "nt"')
def test_get_logging_handler():
    args = Object()
    args.logfile = None
    handler = get_logging_handler(args, ERROR)
    assert isinstance(handler, FileHandler)
    assert handler._filename == DEFAULT_LOGFILE
    assert handler.level == ERROR


def test_set_logging_level():
    logger = Object()
    logger.level_name = None
    args = Object()
    args.verbose = True
    args.debug = False
    new_logger = set_logging_level(args, logger)
    assert new_logger.level_name == INFO
    assert not new_logger.level_name == DEBUG
    args.verbose = False
    args.debug = True
    new_logger = set_logging_level(args, logger)
    assert not new_logger.level_name == INFO
    assert new_logger.level_name == DEBUG
