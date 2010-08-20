'''
Utility functions for creting temporary projects, sources, and templates.
'''

import shutil
import tempfile
from os import path

from swsg.projects import Project
from swsg.sources import Source
from swsg.templates import SimpleTemplate


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

    def add_source(self, text):
        markup = self.project.config.get(
                'local configuration', 'markup language')
        source_filename = path.join(
            self.project.source_dir, 'temp-source.{0}'.format(markup))
        with open(source_filename, 'w') as fp:
            fp.write(text)
        return Source(source_filename)

    def add_template(self, text):
        template_filename = path.join(
            self.project.template_dir, 'temp-template')
        with open(template_filename, 'w') as fp:
            fp.write(text)
        return SimpleTemplate(self.project, template_filename)
