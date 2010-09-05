from os import path
from functools import partial
from datetime import datetime
from ConfigParser import SafeConfigParser, NoSectionError

import py
from swsg.templates import SimpleTemplate

from temp_utils import TemporaryProject


def pytest_funcarg__temp_project(request):
    p = TemporaryProject()
    request.addfinalizer(p.remove)
    return p


def test_make_project_directories(temp_project):
    p = temp_project
    p.make_project_directories()
    path_join = partial(path.join, p.project_dir)
    assert path.exists(p.path)
    assert path.exists(p.project_dir)
    assert path.exists(path_join('sources'))
    assert path.exists(path_join('templates'))
    assert path.exists(path_join('output'))


def test_update_projects_file(temp_project):
    p = temp_project
    p.make_project_directories()
    assert p.created is None
    assert p.last_modified is None
    p.update_projects_file()
    assert p.created is None
    assert isinstance(p.last_modified, datetime)
    p.update_projects_file(new_created=True)
    assert isinstance(p.created, datetime)
    assert isinstance(p.last_modified, datetime)


def test_local_config(temp_project):
    section = 'local configuration'
    has_option = partial(temp_project.config.has_option, section)
    get = partial(temp_project.config.get, section)
    assert isinstance(temp_project.config, SafeConfigParser)
    assert not temp_project.config.has_section(section)
    assert not has_option('markup language')
    assert not has_option('template language')
    py.test.raises(NoSectionError, "get('markup language') == 'rest'")
    py.test.raises(NoSectionError, "get('template language') == 'simple'")
    temp_project.init()
    assert temp_project.config.has_section(section)
    assert has_option('markup language')
    assert has_option('template language')
    assert get('markup language') == 'rest'
    assert get('template language') == 'simple'


def test_update_config(temp_project):
    p = temp_project
    p.init()
    p.update_config(markup_language='markdown', template_language='jinja2')
    section = 'local configuration'
    assert p.config.get(section, 'markup language') == 'markdown'
    assert p.config.get(section, 'template language') == 'jinja2'


def test_render_project():
    # TODO: test ``Project.render``
    pass


def test_save_template(temp_project):
    template_filename = path.join(temp_project.template_dir, 'temp-template')
    temp_project.init()
    with open(template_filename, 'w') as fp:
        fp.write('<h1>$title</h1><p>$content</p>')
    template = SimpleTemplate(temp_project, template_filename)
    temp_project.save_template(template)
    assert template_filename == path.join(
        temp_project.template_dir, template.filename)
    with open(template_filename) as f:
        assert template.text == f.read()
