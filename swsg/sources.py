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

from swsg.loggers import swsg_logger

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
    def __init__(self, text):
        self.text = text


class ReSTSource(BaseSource):
    def render(self):
        return rest(self.text, writer_name='html')['body']


class CreoleSource(BaseSource):
    def render(self):
        return creole2html.HtmlEmitter(creole.Parser(self.text).parse()).emit()


class TextileSource(BaseSource):
    def render(self):
        # the function textile.textile adds a tab character at the start of the
        # output, so we remove it to normalize the return value
        return textile(self.text).lstrip('\t')


class MarkdownSource(BaseSource):
    def render(self):
        return markdown(self.text, output_format='xhtml')


def get_source_class_by_markup(markup):
    markups = {
        'rest': ReSTSource,
        'creole': CreoleSource,
        'textile': TextileSource,
        'markdown': MarkdownSource}
    try:
        SourceClass = markups[markup]
    except KeyError:
        raise UnsupportedMarkup(markup)
    else:
        return SourceClass


def ensure_markup_is_valid_and_installed(markup_language, logger=swsg_logger):
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
        logger.critical('The package "{0}" is not installed.'.format(
            missing_package))
