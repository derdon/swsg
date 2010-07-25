import os
import shelve
import contextlib
from datetime import datetime
from functools import partial
from itertools import izip
from ConfigParser import SafeConfigParser

from swsg.templates import SimpleTemplate

XDG_DATA_HOME = os.getenv(
    'XDG_DATA_HOME', os.path.expanduser(os.path.join('~', '.local', 'share'))
)
PROJECT_DATA_DIR = os.path.join(XDG_DATA_HOME, 'swsg')
PROJECTS_FILE_NAME = os.path.join(PROJECT_DATA_DIR, 'projects.shelve')

class Project(object):
    CONFIG_SECTION = 'local configuration'

    def __init__(self, path, name):
        self.path = os.path.abspath(path)
        # TODO: be aware of non-ASCII characters in ``name`` and filter only
        # the ASCII characters -> ask Trundle for his nice function :)
        self.name = name
        self.config = SafeConfigParser()

        # there is no empty value for datetime.datetime, so ``None`` is used
        self.created = None
        self.last_modified = None

        # the following values can currently only be changed by subclassing
        # this class
        self.project_dir = os.path.join(self.path, self.name)
        self.source_dir = os.path.join(self.project_dir, 'sources')
        self.template_dir = os.path.join(self.project_dir, 'templates')
        self.output_dir = os.path.join(self.project_dir, 'output')
        self.config_filename = os.path.join(self.project_dir, 'config.ini')

    def __repr__(self):
        return '{0} "{1}"'.format(self.__class__.__name__, self.name)

    def init(self):
        '''create the specific project directory and add a configuration file
        with default values
        
        '''
        self.make_project_directories()
        self.reset_config()
        self.read_config()
        self.update_projects_file(new_created=True)

    def make_project_directories(self):
        for path_name in (self.source_dir, self.template_dir, self.output_dir):
            os.makedirs(path_name)

    @property
    def sources(self):
        self.read_config()
        markup = self.config.get(self.CONFIG_SECTION, 'markup language')
        for source_name in os.listdir(self.source_dir):
            yield Source(source_name, markup)

    @property
    def templates(self):
        self.read_config()
        template_language = self.config.get(
            self.CONFIG_SECTION, 'template language'
        )
        TemplateClass = {
            'simple': SimpleTemplate
        }[template_language]
        for template_name in os.listdir(self.template_dir):
            filename = os.path.join(self.template_dir, template_name)
            yield TemplateClass(self, filename)

    def update_projects_file(self, new_created=False):
        now = datetime.now()
        if new_created:
            self.created = now
        self.last_modified = now
        with contextlib.closing(shelve.open(PROJECTS_FILE_NAME)) as projects:
            projects[self.project_dir] = self

    def read_config(self):
        with open(self.config_filename) as fp:
            self.config.readfp(fp)

    def reset_config(self):
        options = ['markup language', 'template language']
        default_values = ['rest', 'simple']
        default_settings = izip(options, default_values)
        try:
            self.config.add_section(self.CONFIG_SECTION)
        except DuplicateSectionError:
            # the sectiion does already exist, so it will be removed including
            # all its entries
            self.config.remove_section(self.CONFIG_SECTION)
            for option in options:
                self.config.remove_option(self.CONFIG_SECTION, option)
        for option, value in default_settings:
            self.config.set(self.CONFIG_SECTION, option, value)
        with open(os.path.join(self.project_dir, 'config.ini'), 'w') as fp:
            self.config.write(fp)

    def update_config(self, markup_language=None, template_language=None):
        '''Set the values for "markup language" and "template language" to
        ``markup_language`` or ``template_language``, respectively. If one of
        the arguments is None (the default), its corresponding value in the
        configuration file won't change.
        
        '''
        self.read_config()
        options = ('markup language', 'template language')
        values = (markup_language, template_language)
        for option, value in izip(options, values):
            if value is not None:
                self.config.set(self.CONFIG_SECTION, option, value)
        with open(self.config_filename, 'w') as fp:
            self.config.write(fp)
        self.update_projects_file()

    def render(self):
        for template in self.templates:
            for source, output in template.render():
                head, tail = os.path.split(source.filename)
                filename = os.path.splitext(tail)[0]
                output_path = os.path.join(self.output_dir, filename) + '.html'
                with open(output_path, 'w') as fp:
                    fp.write(output)

    def save_source(self, source):
        filename = os.path.join(self.source_dir, source.filename)
        with open(filename, 'w') as fp:
            fp.write(source.text)
        self.update_projects_file()

    def save_template(self, template):
        filename = os.path.join(self.template_dir, template.filename)
        with open(filename, 'w') as fp:
            fp.write(template.text)
        self.update_projects_file()

def iter_projects():
    'Yield all ``Project`` instances which can be found in the projects file'
    with contextlib.closing(shelve.open(PROJECTS_FILE_NAME)) as projects:
        for project in projects.itervalues():
            yield project
