#!/usr/bin/env python

from __future__ import print_function

import sys
import codecs
from os import path, getcwd, name as operating_system
from itertools import imap, izip

from argparse import ArgumentParser
from texttable import Texttable
from py.io import TerminalWriter
from logbook import FileHandler, INFO, DEBUG, ERROR
from progressbar import ProgressBar

from swsg import __version__
from swsg.loggers import swsg_logger as logger
from swsg.file_paths import LOGFILE as DEFAULT_LOGFILE
from swsg.projects import (DEFAULT_SETTINGS, Project, list_project_instances,
    remove_project)
from swsg.sources import SUPPORTED_MARKUP_LANGUAGES
from swsg.templates import SUPPORTED_TEMPLATE_ENGINES
from swsg.utils import is_none


def get_logging_handler(args, logging_level=ERROR):
    if args.logfile is None:
        if operating_system == 'nt':
            # FIXME: use the handler logbook.NTEventLogHandler for windows
            #        users
            raise OSError(
                'Windows is an operating system which is not supported yet. '
                'Install a POSIX compatible system and try again.')
        logfile = DEFAULT_LOGFILE
    else:
        logfile = args.logfile
    return FileHandler(logfile, level=logging_level)


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


def perform_quickstart(args):
    '''Ask the user for required information to initialize a project with the
    desired configuration automatically.
    '''
    def get_default_template_language():
        for option, default_vale in DEFAULT_SETTINGS['general']:
            if option == 'template language':
                return default_value
    # the following instruction text is copied from
    #http://bitbucket.org/birkenfeld/sphinx/src/tip/sphinx/quickstart.py#cl-788
    print('''Please enter values for the following settings
(just press Enter to accept a default value, if one is given in brackets).''')
    prompts = [
        ('project directory', getcwd()),
        ('name of the project', None),
        'template language', get_default_template_language()]
    answers = []
    for prompt, default_value in prompts:
        try:
            if default_value is None:
                full_prompt = '{0} (required!)'.format(prompt)
            else:
                full_prompt = '{0} [{1}]: '.format(prompt, default_value)
            answer = raw_input(full_prompt) or default_value
            # give the user a 2nd chance to enter a value if the default value
            # is None and the user hit enter anyway
            if answer is None:
                print('Error: the {0} is required'.format(prompt))
                answer = raw_input(prompt)
                if not answer:
                    raise EOFError
            answers.append(answer)
        except EOFError:
            sys.exit('interrupted')

    template_language = answers.pop()
    project = Project(*answers)

    template_specific_prompts = DEFAULT_SETTINGS.get(template_language, [])
    template_specific_answers = []
    for option, default_value in template_specific_prompts:
        try:
            answer = raw_input(option) or default_value
            template_specific_answers.append(answer)
        except EOFError:
            sys.exit('interrupted')
    project.init()
    project.update_config(
        template_language,
        izip(template_specific_prompts, template_specific_answers))


def init_project(args):
    project = Project(args.project_directory, args.name)
    project.init()


def remove_project_(args):
    project = Project(args.project_directory, args.path)
    remove_project(project)
    print('removed the project {0}'.format(project.project_dir))


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
    project = Project(*path.split(getcwd()))
    project.update_config(
        markup_language=args.markup_language,
        template_language=args.template_language)


def render(args):
    pbar = ProgressBar(maxval=100)
    # the project's directory is the current working directory
    project = Project(*path.split(getcwd()))
    for i, (output_path, output) in enumerate(project.render()):
        with codecs.open(output_path, 'w', 'utf-8') as fp:
            fp.write(output)
        pbar.update(i + 1)


def parse_args(argv=sys.argv[1:]):
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
        'list-projects', help='List all projects in a fancy ASCII table.')
    list_parser.set_defaults(func=print_list_of_projects)
    quickstart_parser = subparsers.add_parser(
        'quickstart',
        help=('answer some questions to get a '
        'ready-to-use project with your desired settings'))
    quickstart_parser.set_defaults(func=perform_quickstart)
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
        'path',
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
    level = set_logging_level(args, logger)
    handler = get_logging_handler(args, level)
    with handler.applicationbound():
        args.func(args)

if __name__ == '__main__':
    main()
