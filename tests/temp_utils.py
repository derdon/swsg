'''
Utility functions for creting temporary projects, sources, and templates.
'''

import shutil
import tempfile
from os import path

from swsg.projects import Project
from swsg.sources import Source
from swsg.templates import (SUPPORTED_TEMPLATE_ENGINES,
    SimpleTemplate, MakoTemplate, Jinja2Template, GenshiTemplate)


class TemporaryProject(Project):
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        self.project = Project(*path.split(self.temp_dir))

    def __getattr__(self, name):
        return getattr(self.project, name)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        shutil.rmtree(self.temp_dir)

    def remove(self):
        'remove the temporary project manually'
        shutil.rmtree(self.temp_dir)

    def add_source(self, text, markup='rest'):
        source_filename = path.join(
            self.project.source_dir, 'temp-source.{0}'.format(markup))
        with open(source_filename, 'w') as fp:
            fp.write(text)
        return Source(text, markup)

    def add_template(self, text, template_engine='simple'):
        template_filename = path.join(
            self.project.template_dir, 'temp-template')
        with open(template_filename, 'w') as fp:
            fp.write(text)
        try:
            TemplateClass = {
                'simple': SimpleTemplate,
                'mako': MakoTemplate,
                'jinja2': Jinja2Template,
                'genshi': GenshiTemplate}[template_engine]
        except KeyError:
            raise ValueError(
                'the argument "template_engine" must '
                'be one of the following value: {0}'.format(
                    ', '.join(SUPPORTED_TEMPLATE_ENGINES)))
        return TemplateClass(self.project, template_filename)
