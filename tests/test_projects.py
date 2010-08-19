from os import path
from functools import partial
from datetime import datetime
from ConfigParser import SafeConfigParser, NoSectionError

import py
from swsg.templates import SimpleTemplate

from temp_utils import TemporaryProject


def test_make_project_directories():
    project = TemporaryProject()
    with project as p:
        p.make_project_directories()
        path_join = partial(path.join, p.project_dir)
        assert path.exists(p.path)
        assert path.exists(p.project_dir)
        assert path.exists(path_join('sources'))
        assert path.exists(path_join('templates'))
        assert path.exists(path_join('output'))


def test_update_projects_file():
    project = TemporaryProject()
    with project as p:
        p.make_project_directories()

        assert p.created is None
        assert p.last_modified is None

        p.update_projects_file()

        assert p.created is None
        assert isinstance(p.last_modified, datetime)

        p.update_projects_file(new_created=True)

        assert isinstance(p.created, datetime)
        assert isinstance(p.last_modified, datetime)


def test_local_config():
    project = TemporaryProject()
    section = 'local configuration'
    has_option = partial(project.config.has_option, section)
    get = partial(project.config.get, section)

    with project as p:
        assert isinstance(p.config, SafeConfigParser)
        assert not p.config.has_section(section)
        assert not has_option('markup language')
        assert not has_option('template language')
        py.test.raises(NoSectionError, "get('markup language') == 'rest'")
        py.test.raises(NoSectionError, "get('template language') == 'simple'")

        p.init()

        assert p.config.has_section(section)
        assert has_option('markup language')
        assert has_option('template language')
        assert get('markup language') == 'rest'
        assert get('template language') == 'simple'


def test_update_config():
    project = TemporaryProject()
    with project as p:
        p.init()
        p.update_config(markup_language='markdown', template_language='jinja2')
        section = 'local configuration'
        assert p.config.get(section, 'markup language') == 'markdown'
        assert p.config.get(section, 'template language') == 'jinja2'


def test_render_project():
    # TODO: test ``Project.render``
    pass


def test_save_template():
    project = TemporaryProject()
    template_filename = path.join(project.template_dir, 'temp-template')
    with project as p:
        p.init()
        with open(template_filename, 'w') as fp:
            fp.write('<h1>$title</h1><p>$content</p>')
        template = SimpleTemplate(project, template_filename)
        p.save_template(template)

        assert template_filename == path.join(
            p.template_dir, template.filename)
        with open(template_filename) as f:
            assert template.text == f.read()
