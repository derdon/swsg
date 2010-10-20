from os import path
from functools import partial
from datetime import datetime
from ConfigParser import SafeConfigParser, NoSectionError

import py
from swsg.sources import ReSTSource
from swsg.templates import SimpleTemplate
from swsg.projects import Project, remove_project, NonexistingProject

from test_templates import SIMPLE_TEMPLATE_TEXT

SOURCE_CONTENT = (
    u'headline\n'
    u'--------\n'
    u'*important* text'
)


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


def test_sources_property(temp_project):
    temp_project.init()
    list_of_sources = list(temp_project.sources)
    assert list_of_sources == []
    make_source = py.path.local(temp_project.source_dir).ensure
    source1 = make_source('source1.rest')
    source1.check(file=True)
    source1_content = 'content of source1'
    source1.write(source1_content)
    source2 = make_source('source2.rest')
    source2.check(file=True)
    source2_content = 'content of source2'
    source2.write(source2_content)
    list_of_sources = list(temp_project.sources)
    assert len(list_of_sources) == 2
    assert list_of_sources == [
        ReSTSource(source1_content),
        ReSTSource(source2_content)]


def test_templates_property(temp_project):
    temp_project.init()
    list_of_templates = list(temp_project.templates)
    assert list_of_templates == []
    make_template = py.path.local(temp_project.template_dir).ensure
    template1 = make_template('template1.html')
    template1.check(file=True)
    template1_content = 'content of template1'
    template1.write(template1_content)
    template2 = make_template('template2.html')
    template2.check(file=True)
    template2_content = 'content of template2'
    template2.write(template2_content)
    list_of_templates = list(temp_project.templates)
    assert len(list_of_templates) == 2
    assert list_of_templates == [
        (
            SimpleTemplate(template1_content),
            path.join(temp_project.template_dir, str(template1))),
        (
            SimpleTemplate(template2_content),
            path.join(temp_project.template_dir, str(template2)))]


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
    section = 'general'
    has_option = partial(temp_project.config.has_option, section)
    get = partial(temp_project.config.get, section)
    assert isinstance(temp_project.config, SafeConfigParser)
    assert not temp_project.config.has_section(section)
    assert not has_option('template language')
    py.test.raises(NoSectionError, "get('template language') == 'simple'")
    temp_project.init()
    assert temp_project.config.has_section(section)
    assert has_option('template language')
    assert get('template language') == 'simple'


def test_update_config(temp_project):
    temp_project.init()
    section = 'general'
    temp_project.update_config(section, [('template language', 'jinja2')])
    assert temp_project.config.get(section, 'template language') == 'jinja2'


def test_render_project(temp_project):
    temp_project.init()
    source_path = py.path.local(
        temp_project.source_dir).ensure('temp-source.rest')
    source_path.check(file=True)
    source_path.write(SOURCE_CONTENT)
    template_path = py.path.local(
        temp_project.template_dir).ensure('template.html')
    template_path.check(file=True)
    template_path.write(SIMPLE_TEMPLATE_TEXT)
    list_of_templates = list(temp_project.templates)
    assert len(list(temp_project.sources)) == 1
    assert len(list_of_templates) == 1

    template, template_path = list_of_templates[0]
    return_values = temp_project.render()
    output_path, output = return_values.next()
    source_name, rendered_template = template.render(
        temp_project.source_dir).next()
    assert source_name == 'temp-source.rest'
    assert output == rendered_template
    assert output_path == path.join(
        temp_project.output_dir, 'temp-source.html')
    # there is only one template which assigns to only one source, so there
    # shouldn't be anything left in the generator
    py.test.raises(StopIteration, 'return_values.next()')


def test_save_source(temp_project):
    assert not temp_project.updated_projects_file
    temp_project.init()
    # set ``updated_projects_file`` to False to check whether it is set to True
    # after calling ``save_source``
    temp_project.updated_projects_file = False
    source_filename = 'temp-source'
    absolute_source_filename = path.join(
        temp_project.source_dir, source_filename)
    source = ReSTSource(SOURCE_CONTENT)
    temp_project.save_source(source, source_filename)
    assert temp_project.updated_projects_file
    with open(absolute_source_filename) as fp:
        assert SOURCE_CONTENT == fp.read()


def test_save_template(temp_project):
    assert not temp_project.updated_projects_file
    temp_project.init()
    # set ``updated_projects_file`` to False to check whether it is set to True
    # after calling ``save_source``
    temp_project.updated_projects_file = False
    template_content = 'the template text'
    template_filename = 'template.html'
    absolute_template_filename = path.join(
        temp_project.template_dir, template_filename)
    template = SimpleTemplate(template_content)
    temp_project.save_template(template, template_filename)
    assert temp_project.updated_projects_file
    with open(absolute_template_filename) as fp:
        assert template_content == fp.read()


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
