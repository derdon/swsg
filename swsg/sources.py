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

from swsg import swsg_logger as logger


class Source(object):
    POSSIBLE_MARKUP_LANGUAGES = frozenset(
        ['rest', 'creole', 'textile', 'markdown'])

    def __init__(self, text, markup_language):
        self.text = text
        self.markup_language = markup_language
        if self.markup_language not in self.POSSIBLE_MARKUP_LANGUAGES:
            raise ValueError(
                '{0} is not an allowed value for "markup_language"; '
                'possible valid values are: {1}'.format(
                    self.markup_language,
                    self.POSSIBLE_MARKUP_LANGUAGES))
        elif self.markup_language not in installed_markups:
            if self.markup_language == 'rest':
                missing_package = 'docutils'
            else:
                missing_package = self.markup_language
            logger.critical('The package "{0}" is not installed.'.format(
                missing_package))

    def render(self):
        # FIXME: normalize output so that the user can decide whether to use
        # HTML or XHTML
        markups = {
            'rest': render_rest,
            'creole': render_creole,
            'textile': render_textile,
            'markdown': render_markdown}
        render_func = markups[self.markup_language]
        return render_func(self.text)


def render_rest(text):
    return rest(text, writer_name='html')['body']


def render_creole(text):
    return creole2html.HtmlEmitter(creole.Parser(text).parse()).emit()


def render_textile(text):
    # the function textile.textile adds a tab character at the start of the
    # output, so we remove it to normalize the return value
    return textile(text).lstrip('\t')


def render_markdown(text):
    return markdown(text, output_format='xhtml')
