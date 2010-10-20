import os
import shutil
import shelve
import contextlib
from datetime import datetime
from itertools import izip
from ConfigParser import SafeConfigParser, DuplicateSectionError

from swsg.loggers import swsg_logger as logger
from swsg.file_paths import DEFAULT_PROJECTS_FILE_NAME
from swsg.templates import (SimpleTemplate, MakoTemplate, Jinja2Template,
    GenshiTemplate, get_template_class_by_template_language)
from swsg.sources import get_source_class_by_markup


class NonexistingProject(Exception):
    pass


class Project(object):

    def __init__(self, path, name,
                 projects_file_name=DEFAULT_PROJECTS_FILE_NAME):
        self.path = os.path.abspath(path)
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
        self.projects_file_name = projects_file_name

        # True after the projects file was updated
        self.updated_projects_file = False

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
        logger.notice('creating project directories')
        for path_name in (self.source_dir, self.template_dir, self.output_dir):
            logger.info('creating the directory {0}'.format(path_name))
            os.makedirs(path_name)

    @property
    def exists(self):
        dir_paths = (
            self.project_dir, self.source_dir,
            self.template_dir, self.output_dir
        )
        file_paths = (self.config_filename, self.projects_file_name)
        paths = dir_paths + file_paths
        return (
            all(os.path.exists(path) for path in paths) and
            all(os.path.isdir(dir_path) for dir_path in dir_paths) and
            all(os.path.isfile(file_path) for file_path in file_paths) and
            self.updated_projects_file
        )

    @property
    def sources(self):
        for source_name in os.listdir(self.source_dir):
            # the markup language is the filename extension without the dot.
            # For example, the content of "foo.rest" will be rendered as ReST
            markup_language = os.path.splitext(source_name)[1].lstrip('.')
            source_path = os.path.join(self.source_dir, source_name)
            with open(source_path) as fp:
                text = fp.read().decode('utf-8')
            SourceClass = get_source_class_by_markup(markup_language)
            yield SourceClass(text)

    @property
    def templates(self):
        self.read_config()
        template_language = self.config.get('general', 'template language')
        try:
            TemplateClass = get_template_class_by_template_language(
                template_language)
        except UnsupportedTemplate, e:
            logger.critical(str(e))
        for template_name in os.listdir(self.template_dir):
            filename = os.path.join(self.template_dir, template_name)
            with open(filename) as fp:
                file_content = fp.read().decode('utf-8')
            yield TemplateClass(file_content), filename

    def update_projects_file(self, new_created=False):
        now = datetime.now()
        if new_created:
            logger.notice(
                'creating the projects file {0}'.format(
                    self.projects_file_name))
            self.created = now
        self.last_modified = now
        with contextlib.closing(shelve.open(self.projects_file_name)) as p:
            logger.notice(
                'updating the projects file {0}'.format(
                    self.projects_file_name))
            p[self.project_dir] = self
        self.updated_projects_file = True

    def read_config(self):
        logger.notice('reading the configuration file')
        with open(self.config_filename) as fp:
            self.config.readfp(fp)

    def reset_config(self):
        logger.notice('resetting the configuration file')
        default_settings = {
            'general':
                [('template language', 'simple')],
            'genshi':
                [
                    # can be either 'htlm' or 'xhtml'. every other doesn't make
                    # any sense for swsg
                    ('method', 'html'),
                    # can be one of the following values listed in this link:
                    # http://genshi.edgewall.org/browser/trunk/genshi/output.py#L82
                    ('doctype', 'html5')]}
        for section, config_items in default_settings.iteritems():
            if not self.config.has_section(section):
                logger.info('add the section {0}'.format(section))
                self.config.add_section(section)
            for option, value in config_items:
                logger.info(
                    'section {0}: setting the option {1} '
                    'to the value {2}'.format(section, option, value))
                self.config.set(section, option, value)
        with open(self.config_filename, 'w') as fp:
            self.config.write(fp)

    def update_config(self, section, config_items):
        '''Change the given values of ``config_items`` (a list of tuples) in
        the section ``section`` and write them into the configuration file
        ``self.config_filename``.

        '''
        self.read_config()
        for option, value in config_items:
            logger.info(
                'section {0}: setting the option {1} to the value {2}'.format(
                    section, option, value))
            self.config.set(section, option, value)
        with open(self.config_filename, 'w') as fp:
            self.config.write(fp)
        # FIXME: call ``self.update_projects_file()``
        self.updated_projects_file = True

    def render(self):
        logger.notice('starting the rendering process')
        for template, template_filename in self.templates:
            try:
                rendered_templates = template.render(self.source_dir)
            except NonexistingSource, e:
                logger.critical(str(e))
            else:
                for source_name, output in rendered_templates:
                    head, tail = os.path.split(source_name)
                    filename = os.path.splitext(tail)[0]
                    output_path = os.path.join(
                        self.output_dir, filename) + '.html'
                    logger.info('{0} + {1} -> {2}'.format(
                        source_name, template_filename, output_path))
                    yield output_path, output
        logger.notice('finishing the rendering process')

    def save_source(self, source, name):
        logger.notice('saving the source {0} in the directory {1}'.format(
            name, self.source_dir))
        filename = os.path.join(self.source_dir, name)
        with open(filename, 'w') as fp:
            fp.write(source.text)
        self.update_projects_file()

    def save_template(self, template, name):
        logger.notice('saving the template {0} in the directory {1}'.format(
            name, self.template_dir))
        filename = os.path.join(self.template_dir, name)
        with open(filename, 'w') as fp:
            fp.write(template.text)
        self.update_projects_file()


def list_project_instances(projects_file_name=DEFAULT_PROJECTS_FILE_NAME):
    'get all ``Project`` instances which can be found in the projects file'
    with contextlib.closing(shelve.open(projects_file_name)) as projects:
        return projects.values()


def remove_project(project):
    '''remove both the project's directory and its entry in the projects file

    '''
    proj_dir = project.project_dir
    if project.exists:
        shutil.rmtree(proj_dir)
        with contextlib.closing(shelve.open(project.projects_file_name)) as p:
            p.pop(proj_dir)
    else:
        # project does not exist, therefore it cannot be removed
        raise NonexistingProject(
            'The project {0} with its belonging '
            'directory {1} does not exist.'.format(project, proj_dir))
