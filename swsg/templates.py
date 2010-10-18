import string
from os import path

from swsg.sources import (ensure_markup_is_valid_and_installed,
    get_source_class_by_markup)


SUPPORTED_TEMPLATE_ENGINES = frozenset(['simple', 'mako', 'jinja2', 'genshi'])


class NonexistingSource(Exception):
    def __init__(self, source_path):
        self.source_path = source_path

    def __str__(self):
        return 'the source {0} does not exist'.format(self.source_path)

    def __repr__(self):
        return '{0}({1})'.format(self.__class__.__name__, self.source_path)


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
            # the filename mentioned in the template does not exist
            # -> raise a custom exception
            try:
                with open(filename) as fp:
                    text = fp.read().decode('utf-8')
            except IOError:
                raise NonexistingSource(filename)
            SourceClass = get_source_class_by_markup(markup_language)
            yield SourceClass(text), source_name

    def get_namespace(self, source):
        rendered_source_text = source.render()
        return {
            'title': source.title,
            'content': rendered_source_text}

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
            template = string.Template(self.text)
            rendered_template = template.safe_substitute(
                **self.get_namespace(source))
            yield source_name, rendered_template


class MakoTemplate(BaseTemplate):
    def render(self, source_path):
        # import mako only here because this package is optional
        from mako.template import Template
        for source, source_name in self.get_sources(source_path):
            template = Template(self.text)
            rendered_template = template.render(**self.get_namespace(source))
            yield source_name, rendered_template


class Jinja2Template(BaseTemplate):
    def render(self, source_path):
        raise NotImplementedError


class GenshiTemplate(BaseTemplate):
    def render(self, source_path):
        raise NotImplementedError
