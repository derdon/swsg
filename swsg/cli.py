#!/usr/bin/env python

import sys
from os import path

from argparse import ArgumentParser
from texttable import Texttable
from py.io import TerminalWriter
from swsg import __version__
from swsg.projects import Project, iter_projects

'''
swsg-cli quickstart

    -> ask for the following values:
           - configuration values (markup language, template language)
           - project name
           - project path
'''

# TODO: more output so that the user can see something happens

def list_projects(args):
    terminal_writer = TerminalWriter()
    terminal_width = terminal_writer.fullwidth
    table = Texttable(max_width=terminal_width)
    table.header(['Name', 'Path', 'Created', 'Last modified'])
    for p in iter_projects():
        table.add_row([
            p.name, p.path,
            p.created.strftime('%c'), p.last_modified.strftime('%c')
        ])
    print table.draw()

def init_project(args):
    project = Project(args.project_directory, args.name)
    project.init()

def change_config(args):
    # the project's directory is the current working directory
    project = Project(*path.split(path.abspath(path.curdir)))
    project.update_config(
        markup_language=args.markup_language,
        template_language=args.template_language
    )

def render(args):
    # the project's directory is the current working directory
    project = Project(*path.split(path.abspath(path.curdir)))
    project.render()

def parse_args(argv=sys.argv[1:]):
    # TODO: add help strings to each argument
    # TODO: improve the help by using the method ``parser.add_argument_group``
    #       which groups the help message by subarguments
    parser = ArgumentParser()
    parser.add_argument(
        '-v', '--version', action='version', version='%(prog)s ' + __version__
    )
    subparsers = parser.add_subparsers()

    list_parser = subparsers.add_parser('list')
    list_parser.set_defaults(func=list_projects)

    init_parser = subparsers.add_parser('init')
    init_parser.add_argument('name')
    init_parser.add_argument('-p', '--project-directory', default='.')
    init_parser.set_defaults(func=init_project)

    config_parser = subparsers.add_parser('change-config')
    config_parser.add_argument('-m', '--markup-language')
    config_parser.add_argument('-t', '--template-language')
    config_parser.set_defaults(func=change_config)

    render_parser = subparsers.add_parser('render')
    render_parser.add_argument('-f', '--force-all')
    render_parser.set_defaults(func=render)

    return parser.parse_args(argv)

def main(argv=sys.argv[1:]):
    args = parse_args(argv)
    args.func(args)

if __name__ == '__main__':
    main()
