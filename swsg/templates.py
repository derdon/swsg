import codecs
import string
from os import path

from swsg.sources import Source


SUPPORTED_TEMPLATE_ENGINES = frozenset(['simple', 'mako', 'jinja2', 'genshi'])

class BaseTemplate(object):
    def __init__(self, project, filename):
        self.project = project
        self.filename = filename
        with codecs.open(self.filename, 'r', 'utf-8') as fp:
            first_line = fp.readline()
            rest = fp.read()
        # the directive "sources" is optional. Therefore, the first line is
        # checked whether it starts whith the string "sources:". If it does,
        # the string after "sources:" is first stripped by whitespace and then
        # splitted up by commas to get the file names which belong to the given
        # template
        if first_line.startswith('sources:'):
            self.source_names = (
                first_line.lstrip('sources:').strip().split(','))
            self.text = rest
        else:
            self.source_names = []
            self.text = first_line + rest

    def __repr__(self):
        return '{0} "{1}"'.format(self.__class__.__name__, self.filename)

    @property
    def sources(self):
        for source_name in self.source_names:
            filename = path.join(self.project.source_dir, source_name)
            # FIXME: it could be that this filename does not exist, i.e. an
            # IOError will be raised then! -> What should happen in this case?
            yield Source(filename)

    def render(self, source):
        raise NotImplementedError


class SimpleTemplate(BaseTemplate):
    'Render templates as described in :pep:`0292`'
    def render(self):
        for source in self.sources:
            rendered_source_text = source.render()
            template = string.Template(self.text)
            # get the "pure" filename of the source, i.e. no absolute path
            # and no file extension
            source_title = path.splitext(path.split(source.filename)[1])[0]
            rendered_template = template.safe_substitute(
                title=source_title,
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
