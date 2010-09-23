#!/usr/bin/env python

from __future__ import print_function

import sys
import platform
from os import path
from itertools import imap

from argparse import ArgumentParser
from texttable import Texttable
from py.io import TerminalWriter
from logbook import FileHandler, INFO, DEBUG

from swsg import __version__
from swsg.loggers import swsg_logger as logger
from swsg.file_paths import LOGFILE as DEFAULT_LOGFILE
from swsg.projects import Project, list_project_instances
from swsg.sources import SUPPORTED_MARKUP_LANGUAGES
from swsg.templates import SUPPORTED_TEMPLATE_ENGINES
from swsg.utils import is_none


def get_logging_handler(args):
    if args.logfile is None:
        if platform.system() == 'Windows':
            # FIXME: use the handler logbook.NTEventLogHandler for windows
            #        users
            raise OSError(
                'Windows is an operating system which is not supported yet. '
                'Install a POSIX compatible system and try again.')
        logfile = DEFAULT_LOGFILE
    else:
        logfile = args.logfile
    return FileHandler(logfile)


def format_list_of_projects():
    terminal_writer = TerminalWriter()
    terminal_width = terminal_writer.fullwidth
    table = Texttable(max_width=terminal_width)
    table.header(['Name', 'Path', 'Created', 'Last modified'])
    projects = list_project_instances()
    for p in projects:
        table.add_row([
            p.name, p.path,
            p.created.strftime('%c'), p.last_modified.strftime('%c')])
    return table.draw() if projects else "no project created yet"


def print_list_of_projects(args):
    print(format_list_of_projects())


def init_project(args):
    project = Project(args.project_directory, args.name)
    project.init()


def remove_project(args):
    raise NotImplementedError


def validate_change_config(args):
    # at least one of the options must be given (otherwise, the file is only
    # touched but not edited)
    conf_values = [args.markup_language, args.template_language]
    if all(imap(is_none, conf_values)):
        print(
            'Error: Neither a markup language '
            'nor a template language was given.',
            file=sys.stderr)
        # the exit code 2 is used for CLI errors by convention
        sys.exit(2)


def change_config(args):
    # the project's directory is the current working directory
    project = Project(*path.split(path.abspath(path.curdir)))
    project.update_config(
        markup_language=args.markup_language,
        template_language=args.template_language)


def render(args):
    # the project's directory is the current working directory
    # TODO: add a progressbar
    project = Project(*path.split(path.abspath(path.curdir)))
    project.render()


def parse_args(argv=sys.argv[1:]):
    # TODO: improve the help by using the method ``parser.add_argument_group``
    #       which groups the help message by subarguments
    parser = ArgumentParser()
    parser.add_argument(
        '-v', '--verbose', action='store_true',
        help=(
            'Enable verbosity mode (disabled per default). Log more logging '
            'messages as usual, but no debugging messages.'))
    parser.add_argument(
        '-d', '--debug', action='store_true',
        help=(
            'Enable debugging mode (disabled per default). This option causes '
            'SWSG to log as many messages as possible and therefore overrides '
            'the option "verbose".'))
    parser.add_argument(
        '--version', action='version', version='%(prog)s ' + __version__)
    parser.add_argument('-l', '--logfile')
    subparsers = parser.add_subparsers()
    list_parser = subparsers.add_parser(
        'list', help='List all projects in a fancy ASCII table.')
    list_parser.set_defaults(func=print_list_of_projects)

    init_parser = subparsers.add_parser(
        'init', help='create and initialize a new project')
    init_parser.add_argument('name', help='The name of the project')
    init_parser.add_argument(
        '-p', '--project-directory', default='.',
        help=(
            'The directory where the new project will be created. It must '
            'already exist before the calling this command.'))
    init_parser.set_defaults(func=init_project)
    remove_parser = subparsers.add_parser(
        'remove-project', help='remove a project which does already exist')
    remove_parser.add_argument(
        'project',
        help='The path to the project directory which will be removed')
    remove_parser.set_defaults(func=remove_project)
    config_parser = subparsers.add_parser(
        'change-config',
        help=(
            'Change project-dependent configuration values. It is recommended '
            'to use this interface instead of editing the configuration file '
            'config.ini directly.'))
    config_parser.add_argument(
        '-m', '--markup-language', choices=SUPPORTED_MARKUP_LANGUAGES,
        help=(
            'The name of the markup language being used. Possible valid values'
            ' are: {0}'.format(', '.join(SUPPORTED_MARKUP_LANGUAGES))))
    config_parser.add_argument(
        '-t', '--template-language', choices=SUPPORTED_TEMPLATE_ENGINES,
        help=(
            'The name of the template engine being used. Possible valid values'
            ' are: {0}'.format(', '.join(SUPPORTED_TEMPLATE_ENGINES))))
    config_parser.set_defaults(func=change_config)
    render_parser = subparsers.add_parser(
        'render',
        help=(
            'Render the templates with their corresponding source files which '
            'are located in the current project directory.'))
    render_parser.set_defaults(func=render)
    return parser.parse_args(argv)


def set_logging_level(args, logger):
    if args.verbose:
        logger.level_name = INFO
    if args.debug:
        logger.level_name = DEBUG
    return logger


def main(argv=sys.argv[1:]):
    args = parse_args(argv)
    if args.func == change_config:
        validate_change_config(args)
    local_logger = set_logging_level(args, logger)
    handler = get_logging_handler(args)
    with handler.applicationbound(bubble=False):
        args.func(args)

if __name__ == '__main__':
    main()
