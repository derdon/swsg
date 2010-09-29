from os import path
from functools import partial
from datetime import datetime
from ConfigParser import SafeConfigParser, NoSectionError

import py
from swsg.templates import SimpleTemplate
from swsg.sources import Source
from swsg.projects import Project, remove_project, NonexistingProject


class Object(object):
    pass


def pytest_funcarg__temp_project(request):
    tmpdir = request.getfuncargvalue('tmpdir')
    projects_filename = str(tmpdir.join('projects.shelve'))
    return Project(str(tmpdir), 'test-project', projects_filename)


def test_make_project_directories(temp_project):
    temp_project.make_project_directories()
    path_join = partial(path.join, temp_project.project_dir)
    assert path.exists(temp_project.path)
    assert path.exists(temp_project.project_dir)
    assert path.exists(path_join('sources'))
    assert path.exists(path_join('templates'))
    assert path.exists(path_join('output'))


def test_update_projects_file(temp_project):
    temp_project.make_project_directories()
    assert temp_project.created is None
    assert temp_project.last_modified is None
    temp_project.update_projects_file()
    assert temp_project.created is None
    assert isinstance(temp_project.last_modified, datetime)
    temp_project.update_projects_file(True)
    assert isinstance(temp_project.created, datetime)
    assert isinstance(temp_project.last_modified, datetime)


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
    temp_project.init()
    temp_project.update_config(
        markup_language='markdown', template_language='jinja2')
    section = 'local configuration'
    assert temp_project.config.get(section, 'markup language') == 'markdown'
    assert temp_project.config.get(section, 'template language') == 'jinja2'


def test_render_project(temp_project, monkeypatch):
    template = Object()
    rendered_template = '<h1>A test title</h1><p>the test content</p>'
    template.render = lambda: [[source, rendered_template]]
    template.filename = 'test-template'
    monkeypatch.setattr(type(temp_project), 'templates', [template])
    temp_project.init()
    source = Object()
    source.filename = 'test-source.rest'
    for output_path, output in temp_project.render():
        expected_output_path = path.join(
            temp_project.output_dir,
            path.splitext(source.filename)[0]) + '.html'
        assert output_path == expected_output_path
        assert output == rendered_template


def test_save_source(temp_project):
    source_content = (
        'headline\n'
        '--------'
        '*important* text'
    )
    source_filename = path.join(temp_project.source_dir, 'temp-source')
    temp_project.init()
    source = Source(source_content, 'rest')
    temp_project.save_source(source, source_filename)
    with open(source_filename) as fp:
        assert source_content == fp.read()


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


def test_project_exists(temp_project):
    assert not temp_project.exists
    temp_project.init()
    assert temp_project.exists


def test_remove_project(temp_project):
    assert not temp_project.exists
    py.test.raises(
        NonexistingProject,
        'remove_project(temp_project)')
    temp_project.init()
    assert temp_project.exists
    remove_project(temp_project)
    assert not temp_project.exists
