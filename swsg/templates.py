import string
from os import path

from swsg.sources import (ensure_markup_is_valid_and_installed,
    get_source_class_by_markup)


SUPPORTED_TEMPLATE_ENGINES = frozenset(['simple', 'mako', 'jinja2', 'genshi'])


class BaseTemplate(object):
    def __init__(self, text):
        '''
        Abstract base class for implementing template classes.
        '''
        self.text
        first_line, sep, rest = text.partition('\n')
        # the directive "sources" is optional. Therefore, the first line is
        # checked whether it starts whith the string "sources:". If it does,
        # the string after "sources:" is first stripped by whitespace and then
        # splitted up by commas to get the file names which belong to the given
        # template
        if first_line.startswith('sources:'):
            self.source_names = map(
                unicode.strip,
                first_line.lstrip('sources:').strip().split(','))
            self.text = rest
        else:
            self.source_names = []
            self.text = first_line + rest

    def __repr__(self):
        return '{0} "{1}"'.format(self.__class__.__name__, self.filename)

    def get_sources(self):
        for source_name in self.source_names:
            filename = path.abspath(source_name)
            # the markup language is the filename extension without the dot.
            # For example, the content of "foo.rest" will be rendered as ReST
            markup_language = path.splitext(filename)[1].lstrip('.')
            ensure_markup_is_valid_and_installed(markup_language)
            # FIXME: it could be that this filename does not exist, i.e. an
            # IOError will be raised then! -> raise a custom exception
            with open(filename) as fp:
                text = fp.read().decode('utf-8')
            SourceClass = get_source_class_by_markup(markup_language)
            yield SourceClass(text)

    def render(self, source):
        raise NotImplementedError


class SimpleTemplate(BaseTemplate):
    'Render templates as described in :pep:`0292`'
    def render(self):
        for source_name, source in self.sources:
            rendered_source_text = source.render()
            template = string.Template(self.text)
            rendered_template = template.safe_substitute(
                title=source_name.rsplit('.', 1)[0],
                content=rendered_source_text)
            yield source, rendered_template


class MakoTemplate(BaseTemplate):
    def render(self, source):
        raise NotImplementedError


class Jinja2Template(BaseTemplate):
    def render(self, source):
        raise NotImplementedError


class GenshiTemplate(BaseTemplate):
    def render(self, source):
        raise NotImplementedError
