from os import path

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

from log_functions import log_missing_package

class Source(object):
    POSSIBLE_MARKUP_LANGUAGES = frozenset(
        ['rest', 'creole', 'textile', 'markdown']
    )
    def __init__(self, filename):
        self.filename = filename
        # the markup language is the filename extension without the dot. For
        # example, the content of "foo.rest" will be rendered as ReST
        self.markup_language = path.splitext(filename)[1].lstrip('.')
        if self.markup_language not in self.POSSIBLE_MARKUP_LANGUAGES:
            raise ValueError(
                '{0} is not an allowed value for "markup_language"; '
                'possible valid values are: {1}'.format(
                    self.markup_language,
                    self.POSSIBLE_MARKUP_LANGUAGES
                )
            )
        elif self.markup_language not in installed_markups:
            if self.markup_language == 'rest':
                missing_package = 'docutils'
            else:
                missing_package = self.markup_language
            log_missing_package(missing_package)

        with open(filename) as fp:
            self.text = fp.read()

    def __repr__(self):
        return '{0} "{1}"'.format(self.__class__.__name__, self.filename)

    def render(self):
        # FIXME: normalize output so that the user can decide whether HTML or
        # XHTML will be used
        render_func = {
            'rest': render_rest,
            'creole': render_creole,
            'textile': render_textile,
            'markdown': render_markdown
        }[self.markup_language]
        return render_func(self.text)

def render_rest(text):
    return rest(text, writer_name='html')['body']

def render_creole(text):
    return creole2html.HtmlEmitter(
        creole.Parser(text).parse()
    ).emit()

def render_textile(text):
    # the function textile.textile adds a tab character at the start of the
    # output, so we remove it to normalize the return value
    return textile(text).lstrip('\t')

def render_markdown(text):
    return markdown(text, output_format='xhtml')
