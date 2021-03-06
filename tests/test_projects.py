from os import path
from functools import partial
from datetime import datetime
from ConfigParser import RawConfigParser, NoSectionError

import py
from swsg.sources import ReSTSource
from swsg.templates import SimpleTemplate
from swsg.projects import Project, remove_project, NonexistingProject

from test_templates import SIMPLE_TEMPLATE_TEXT

SOURCE_CONTENT = (
    u'template: foo.html\n'
    u'title: the short title\n'
    u'*important* text'
)


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
        ('source1.rest', ReSTSource('', '', source1_content)),
        ('source2.rest', ReSTSource('', '', source2_content))]


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
    has_option = temp_project.config.has_option
    get = temp_project.config.get
    assert isinstance(temp_project.config, RawConfigParser)
    assert not temp_project.config.has_section('general')
    assert not temp_project.config.has_section('genshi')
    assert not temp_project.config.has_section('jinja')
    assert not has_option('general', 'template language')
    assert not has_option('genshi', 'method')
    assert not has_option('genshi', 'doctype')
    assert not has_option('jinja2', 'block_start_string')
    assert not has_option('jinja2', 'block_end_string')
    assert not has_option('jinja2', 'variable_start_string')
    assert not has_option('jinja2', 'variable_end_string')
    assert not has_option('jinja2', 'comment_start_string')
    assert not has_option('jinja2', 'comment_end_string')
    assert not has_option('jinja2', 'trim_blocks')
    py.test.raises(
        NoSectionError,
        "get('general', 'template language') == 'simple'")
    temp_project.init()
    assert temp_project.config.has_section('general')
    assert temp_project.config.has_section('genshi')
    assert has_option('general', 'template language')
    assert has_option('genshi', 'method')
    assert has_option('genshi', 'doctype')
    assert has_option('jinja', 'block_start_string')
    assert has_option('jinja', 'block_end_string')
    assert has_option('jinja', 'variable_start_string')
    assert has_option('jinja', 'variable_end_string')
    assert has_option('jinja', 'comment_start_string')
    assert has_option('jinja', 'comment_end_string')
    assert has_option('jinja', 'trim_blocks')
    assert get('general', 'template language') == 'simple'
    assert get('genshi', 'method') == 'html'
    assert get('genshi', 'doctype') == 'html5'


def test_update_config(temp_project):
    temp_project.init()
    section = 'general'
    temp_project.update_config(section, [('template language', 'jinja2')])
    assert temp_project.config.get(section, 'template language') == 'jinja2'


def test_render_project(temp_project):
    temp_project.init()
    source_path = py.path.local(
        temp_project.source_dir).ensure('temp-source.rest')
    assert source_path.check(file=True)
    source_path.write(SOURCE_CONTENT)
    template_path = py.path.local(temp_project.template_dir).ensure('foo.html')
    assert template_path.check(file=True)
    template_path.write(SIMPLE_TEMPLATE_TEXT)
    list_of_sources = list(temp_project.sources)
    assert len(list_of_sources) == 1
    source_name, source = list_of_sources[0]
    assert source_name == 'temp-source.rest'
    assert source == ReSTSource(
        temp_project.template_dir, 'default.html', SOURCE_CONTENT)
    return_values = temp_project.render()
    output_path, output = return_values.next()
    assert output_path == path.join(
        temp_project.output_dir, 'temp-source.html')
    expected_rendered_content = '<p><em>important</em> text</p>\n'
    assert output == SIMPLE_TEMPLATE_TEXT.replace(
        '$title', 'the short title').replace(
            '$content', expected_rendered_content)
    # there is only one template which assigns to only one source, so there
    # shouldn't be anything left in the generator
    py.test.raises(StopIteration, 'return_values.next()')


def test_save_source(temp_project):
    assert not temp_project.updated_projects_file
    temp_project.init()
    # set ``updated_projects_file`` to False to check whether it is set to True
    # after calling ``save_source``
    temp_project.updated_projects_file = False
    source_filename = 'temp-source.rest'
    absolute_source_filename = path.join(
        temp_project.source_dir, source_filename)
    source = ReSTSource(
        temp_project.template_dir,
        temp_project.config.get('general', 'default template'),
        SOURCE_CONTENT)
    temp_project.save_source(source, absolute_source_filename)
    assert temp_project.updated_projects_file
    with open(absolute_source_filename) as fp:
        text = fp.read()
    assert SOURCE_CONTENT == text


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
        'remove_project('
        '   temp_project.project_dir,'
        '   temp_project.projects_file_name)')
    temp_project.init()
    assert temp_project.exists
    remove_project(temp_project.project_dir, temp_project.projects_file_name)
    assert not temp_project.exists
