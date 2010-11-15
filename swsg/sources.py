from os import path
from functools import partial

from docutils.core import publish_parts as rest
installed_markups = set(['rest'])
try:
    from markdown import markdown
    installed_markups.add('markdown')
except ImportError:
    pass
try:
    from textile import textile
    installed_markups.add('textile')
except ImportError:
    pass
try:
    import creole
    import creole2html
    installed_markups.add('creole')
except ImportError:
    pass

from swsg import NoninstalledPackage
from swsg.template_functions import clevercss

SUPPORTED_MARKUP_LANGUAGES = frozenset(
    ['rest', 'creole', 'textile', 'markdown'])


class UnsupportedMarkup(Exception):
    def __init__(self, markup):
        self.markup = markup

    def __str__(self):
        return 'the markup {0} is not supported'.format(self.markup)

    def __repr__(self):
        return '{0}({1})'.format(self.__class__.__name__, self.markup)


class BaseSource(object):
    def __init__(self, template_dir, default_template, text):
        splitted_text = text.split('\n', 2)
        try:
            first_line, second_line, rest = splitted_text
            first_lines = [first_line, second_line]
        except ValueError:
            # there is only one newline or no newline at all
            try:
                first_line, rest = splitted_text
                first_lines = [first_line]
            except ValueError:
                # there is no newline in the text, therefore there are no
                # variable assignments
                first_lines = []
                rest = text
        title = ''
        template = ''
        temp_first_lines = first_lines[:]
        for line in first_lines:
            # remove the line from the list of the first two lines where a
            # variable assignment can be found
            if line.startswith('title:'):
                title = line.lstrip('title:').strip()
                temp_first_lines.remove(line)
            elif line.startswith('template:'):
                template = line.lstrip('template:').strip()
                temp_first_lines.remove(line)
        # if the title is not set, "unknown" will be used. That means that
        # setting the title is highly recommended!
        self.title = title or 'unknown'
        # the directive "template" is optional. If it is set, its assigned
        # value is used as the template for this source. Otherwise, the default
        # template will be used
        self.template_path = path.join(
            template_dir,
            template or default_template)
        self.full_text = text
        self.text = '\n'.join(temp_first_lines + [rest])

        try:
            rendered_source = self.render_templateless()
        except NotImplementedError:
            rendered_source = ''
        self.namespace = {
            'title': self.title,
            'content': rendered_source,
            'clevercss': clevercss}

    def __eq__(self, other):
        return type(self) == type(other) and self.full_text == other.full_text

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash(self.full_text)

    def render_templateless(self):
        raise NotImplementedError

    def render(self, TemplateClass, **template_options):
        # render the template with the source's namespace
        with open(self.template_path) as fp:
            text = fp.read().decode('utf-8')
        template = TemplateClass(text)
        return template.render(self.namespace, **template_options)


class ReSTSource(BaseSource):
    def render_templateless(self):
        return rest(self.text, writer_name='html')['body']


class CreoleSource(BaseSource):
    def render_templateless(self):
        return creole2html.HtmlEmitter(creole.Parser(self.text).parse()).emit()


class TextileSource(BaseSource):
    def render_templateless(self):
        # the function textile.textile adds a tab character at the start of the
        # output, so we remove it to normalize the return value
        return textile(self.text).lstrip('\t')


class MarkdownSource(BaseSource):
    def render_templateless(self):
        return markdown(self.text, output_format='xhtml')


def get_source_class_by_markup(markup):
    markups = [
        (frozenset(('rest', 'rst')), ReSTSource),
        (frozenset(('creole',)), CreoleSource),
        (frozenset(('textile', 'tt')), TextileSource),
        (frozenset(('markdown', 'md')), MarkdownSource)]
    for markup_identifiers, SourceClass in markups:
        if markup in markup_identifiers:
            return SourceClass
    raise UnsupportedMarkup(markup)


def ensure_markup_is_valid_and_installed(markup_language):
    if markup_language not in SUPPORTED_MARKUP_LANGUAGES:
        raise ValueError(
            '{0} is not an allowed value for "markup_language"; '
            'possible valid values are: {1}'.format(
                markup_language, SUPPORTED_MARKUP_LANGUAGES))
    elif markup_language not in installed_markups:
        if markup_language == 'rest':
            missing_package = 'docutils'
        else:
            missing_package = markup_language
        raise NoninstalledPackage(missing_package)
