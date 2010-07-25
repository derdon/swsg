import logging

def log_missing_package(pkg_name):
    errmsg = 'The package "{0}" is not installed.'.format(pkg_name)
    logging.error(errmsg)
    # XXX: is exiting really necessary here?
    sys.exit(1)
