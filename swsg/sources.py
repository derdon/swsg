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

from swsg.loggers import swsg_logger as logger

SUPPORTED_MARKUP_LANGUAGES = frozenset(
    ['rest', 'creole', 'textile', 'markdown'])


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
