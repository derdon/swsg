import string

SUPPORTED_TEMPLATE_ENGINES = frozenset(['simple', 'mako', 'jinja2', 'genshi'])

BASE_DEFAULT_TEMPLATE = '''<!DOCTYPE HTML>
<html>
  <head>
    <title>{title}</title>
    {head}
  </head>
  <body>
    {content}
  </body>
</html>'''

DEFAULT_SIMPLE_TEMPLATE = BASE_DEFAULT_TEMPLATE.format(
    title='${title}',
    head='<meta charset="utf-8">',
    content='${content}')

DEFAULT_MAKO_TEMPLATE = DEFAULT_SIMPLE_TEMPLATE

DEFAULT_GENSHI_TEMPLATE = BASE_DEFAULT_TEMPLATE.format(
    title='${title}',
    head='<meta charset="utf-8" />',
    content='${Markup(content)}')

DEFAULT_JINJA_TEMPLATE = BASE_DEFAULT_TEMPLATE.format(
    title='{{ title }}',
    head='<meta charset="utf-8">',
    content='{{ content }}')


class NonexistingSource(Exception):
    def __init__(self, source_path):
        self.source_path = source_path

    def __str__(self):
        return 'the source {0} does not exist'.format(self.source_path)

    def __repr__(self):
        return '{0}({1})'.format(self.__class__.__name__, self.source_path)


class UnsupportedTemplate(Exception):
    def __init__(self, template_language):
        self.template_language = template_language

    def __str__(self):
        return (
            'the template language {0} does either '
            'not exist or is not supported.').format(self.template_language)

    def __repr__(self):
        return '{0}({1})'.format(
            self.__class__.__name__, self.template_language)


class BaseTemplate(object):
    def __init__(self, text):
        '''
        Abstract base class for implementing template classes.
        '''
        self.text = text

    def __eq__(self, other):
        return (type(self) == type(other) and self.text == other.text)

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash(self.text) + hash(tuple(self.source_names))

    def render(self, namespace):
        raise NotImplementedError


class SimpleTemplate(BaseTemplate):
    'Render templates as described in :pep:`0292`'
    def render(self, namespace):
        template = string.Template(self.text)
        return template.safe_substitute(**namespace)


class MakoTemplate(BaseTemplate):
    def render(self, namespace):
        # import mako only here because this package is optional
        from mako.template import Template
        template = Template(self.text)
        return template.render(**namespace)


class Jinja2Template(BaseTemplate):
    def render(self, namespace, **options):
        # import jinja2 only here because this package is optional
        from jinja2 import Environment
        env = Environment(**options)
        template = env.from_string(self.text)
        return template.render(**namespace)


class GenshiTemplate(BaseTemplate):
    def render(self, namespace, **options):
        # import genshi only here because this package is optional
        from genshi.template.markup import MarkupTemplate
        template = MarkupTemplate(self.text)
        stream = template.generate(**namespace)
        # enforce conversion to unicode
        options['encoding'] = None
        rendered_template = stream.render(**options)
        return rendered_template


def get_template_class_by_template_language(template_language):
    normalized_template_language = template_language.lower()
    templates = [
        (frozenset(('simple',)), SimpleTemplate),
        (frozenset(('mako',)), MakoTemplate),
        (frozenset(('jinja', 'jinja2')), Jinja2Template),
        (frozenset(('genshi',)), GenshiTemplate),
    ]
    for template_identifiers, TemplateClass in templates:
        if normalized_template_language in template_identifiers:
            return TemplateClass
    raise UnsupportedTemplate(normalized_template_language)
