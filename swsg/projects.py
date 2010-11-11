import os
import shutil
import shelve
import hashlib
import contextlib
from datetime import datetime
from ConfigParser import RawConfigParser

from swsg.loggers import swsg_logger as logger
from swsg.file_paths import DEFAULT_PROJECTS_FILE_NAME, GLOBAL_CONFIGFILE
from swsg.templates import (SUPPORTED_TEMPLATE_ENGINES,
    DEFAULT_SIMPLE_TEMPLATE, DEFAULT_MAKO_TEMPLATE, DEFAULT_GENSHI_TEMPLATE,
    DEFAULT_JINJA_TEMPLATE, GenshiTemplate, Jinja2Template,
    get_template_class_by_template_language)
from swsg.sources import get_source_class_by_markup
from swsg.utils import hash_file

DEFAULT_SETTINGS = {
    'general':
        [
            ('template language', 'simple'),
            ('default template', 'default.html')],
    'genshi':
        [
            # can be either 'htlm' or 'xhtml'. every other doesn't make
            # any sense for swsg
            ('method', 'html'),
            # can be one of the following values listed in this link:
            # http://genshi.edgewall.org/browser/trunk/genshi/output.py#L82
            ('doctype', 'html5')],
    # see http://jinja.pocoo.org/api/#jinja2.Environment
    'jinja':
        [
            ('block_start_string', '{%'),
            ('block_end_string', '%}'),
            ('variable_start_string', '{{'),
            ('variable_end_string', '}}'),
            ('comment_start_string', '{#'),
            ('comment_end_string', '#}'),
            ('trim_blocks', 'false')]}


class InvalidConfigOption(Exception):
    pass


class NonexistingProject(Exception):
    def __init__(self, project_name):
        self.project_name = project_name

    def __str__(self):
        return ('The project {0!r} does not exist.'.format(self.project_name))

    def __repr__(self):
        return '{0}({1})'.format(self.__class__.__name__, self.project_name)


class Project(object):

    def __init__(self, path, name,
                 projects_file_name=DEFAULT_PROJECTS_FILE_NAME):
        self.path = os.path.abspath(path)
        self.name = name
        # interpolation is not needed, it is only annoying with obscure errors
        # -> take RawConfigParser instead of SafeConfigParser
        self.config = RawConfigParser()

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

        # key is the path to the file, value is its md5 hash
        self.rendered_sources = {}
        self.rendered_templates = {}

        self.config_hash = ''

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
        self.create_default_template()

    def make_project_directories(self):
        logger.notice('creating project directories')
        for path_name in (self.source_dir, self.template_dir, self.output_dir):
            logger.info('creating the directory {0}'.format(path_name))
            os.makedirs(path_name)

    def create_default_template(self):
        self.read_config()
        template_language = self.config.get('general', 'template language')
        default_templates = {
            'simple': DEFAULT_SIMPLE_TEMPLATE,
            'mako': DEFAULT_MAKO_TEMPLATE,
            'genshi': DEFAULT_GENSHI_TEMPLATE,
            'jinja': DEFAULT_JINJA_TEMPLATE
        }
        try:
            default_template = default_templates[template_language]
        except KeyError:
            raise InvalidConfigOption(
                'the option "template language" has to be one of the '
                'following values: ' + ', '.join(SUPPORTED_TEMPLATE_ENGINES))
        default_template_path = os.path.join(self.template_dir, 'default.html')
        with open(default_template_path, 'w') as fp:
            fp.write(default_template)

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
        self.read_config()
        default_template = os.path.join(
            self.template_dir,
            self.config.get('general', 'default template'))
        for source_name in os.listdir(self.source_dir):
            # the markup language is the filename extension without the dot.
            # For example, the content of "foo.rest" will be rendered as ReST
            markup_language = os.path.splitext(source_name)[1].lstrip('.')
            source_path = os.path.join(self.source_dir, source_name)
            with open(source_path) as fp:
                text = fp.read().decode('utf-8')
            SourceClass = get_source_class_by_markup(markup_language)
            yield source_name, SourceClass(
                self.template_dir, default_template, text)

    def update_projects_file(self, new_created=False):
        # create the directories where the projects file will be saved if they
        # does not exist yet
        path, file = os.path.split(self.projects_file_name)
        if not os.path.exists(path):
            logger.notice('creating the directory {0}'.format(path))
            os.makedirs(path)
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
        logger.notice(
            'reading the configuration file {0}'.format(self.config_filename))
        with open(self.config_filename) as fp:
            self.config.readfp(fp)

    def reset_config(self):
        logger.notice(
            'resetting the configuration file {0}'.format(
                self.config_filename))
        # check if thee is a global config in CONFIGDIR
        if os.path.exists(GLOBAL_CONFIGFILE):
            shutil.copyfile(GLOBAL_CONFIGFILE, self.config_filename)
            return None
        for section, config_items in DEFAULT_SETTINGS.iteritems():
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
        self.update_projects_file()

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
        self.update_projects_file()

    def render(self):
        logger.notice('starting the rendering process')
        self.read_config()
        template_language = self.config.get('general', 'template language')
        TemplateClass = get_template_class_by_template_language(
            template_language)
        for source_name, source in self.sources:
            sha256_source = hashlib.sha256(source.full_text).hexdigest()
            template_path = os.path.join(
                self.template_dir, source.template_path)
            sha256_template = hash_file(template_path)
            head, tail = os.path.split(source_name)
            filename = os.path.splitext(tail)[0]
            output_path = os.path.join(self.output_dir, filename) + '.html'
            if source_name in self.rendered_sources:
                # source ehas already been rendered once -> this is a necessary
                # but not sufficient requirement to skip rendering for
                # this source
                if self.rendered_sources.get(output_path) == sha256_source:
                    # source file has not chnaged -> may require rendering if
                    # the configuration file or the source's template has been
                    # changed
                    # compare the new calculated template's hash with the old
                    # one, if it exists. otherwise, rendering will be
                    # necessary
                    source_hash = self.rendered_templates.get(template_path)
                    if source_hash == sha256_template:
                        # check if the config file has been changed since the
                        # last rendering
                        config_hash = hash_file(self.config_filename)
                        if config_hash == self.config_hash:
                            # skip the rendering process, because neither the
                            # source nor its template file nor the config file
                            # have been changed
                            continue
            # pass the config settings of the template language being used
            # if there are settings for it in the config file
            if TemplateClass == GenshiTemplate:
                options = dict(self.config.items('genshi'))
            elif TemplateClass == Jinja2Template:
                options = dict(self.config.items('jinja'))
            else:
                options = {}
            output = source.render(TemplateClass, **options)
            logger.info('{0} + {1} -> {2}'.format(
                source_name, source.template_path, output_path))
            self.rendered_sources[output_path] = sha256_source
            self.rendered_templates[template_path] = sha256_template
            self.config_hash = hash_file(self.config_filename)
            yield output_path, output
        logger.notice('finishing the rendering process')

    def save_source(self, source, name):
        logger.notice('saving the source {0} in the directory {1}'.format(
            name, self.source_dir))
        filename = os.path.join(self.source_dir, name)
        with open(filename, 'w') as fp:
            fp.write(source.full_text)
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


def get_project_by_path(project_dir,
    projects_file_name=DEFAULT_PROJECTS_FILE_NAME):
    full_project_path = os.path.abspath(project_dir)
    with contextlib.closing(shelve.open(projects_file_name)) as p:
        try:
            project = p[full_project_path]
        except KeyError:
            # project does not exist, raise a proper exception
            raise NonexistingProject(project_dir)
        else:
            return project


def remove_project(project_directory,
    projects_file_name=DEFAULT_PROJECTS_FILE_NAME):
    '''remove both the project's directory and its entry in the projects file

    '''
    try:
        shutil.rmtree(project_directory)
    except OSError:
        raise NonexistingProject(project_directory)
    with contextlib.closing(shelve.open(projects_file_name)) as p:
        del p[project_directory]
