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
        self.text = text
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

    def get_sources(self, base_path):
        for source_name in self.source_names:
            filename = path.join(base_path, source_name)
            # the markup language is the filename extension without the dot.
            # For example, the content of "foo.rest" will be rendered as ReST
            markup_language = path.splitext(filename)[1].lstrip('.')
            ensure_markup_is_valid_and_installed(markup_language)
            # FIXME: it could be that this filename does not exist, i.e. an
            # IOError will be raised then! -> raise a custom exception
            with open(filename) as fp:
                text = fp.read().decode('utf-8')
            SourceClass = get_source_class_by_markup(markup_language)
            yield SourceClass(text), source_name

    def __eq__(self, other):
        return (
            type(self) == type(other) and
            self.text == other.text and
            self.source_names == other.source_names)

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash(self.text) + hash(tuple(self.source_names))

    def render(self, source):
        raise NotImplementedError


class SimpleTemplate(BaseTemplate):
    'Render templates as described in :pep:`0292`'
    def render(self, source_path):
        for source, source_name in self.get_sources(source_path):
            rendered_source_text = source.render()
            template = string.Template(self.text)
            rendered_template = template.safe_substitute(
                title=source.title,
                content=rendered_source_text)
            yield source_name, rendered_template


class MakoTemplate(BaseTemplate):
    def render(self, source_path):
        raise NotImplementedError


class Jinja2Template(BaseTemplate):
    def render(self, source_path):
        raise NotImplementedError


class GenshiTemplate(BaseTemplate):
    def render(self, source_path):
        raise NotImplementedError
