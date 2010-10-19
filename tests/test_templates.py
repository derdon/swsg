import py.test
from swsg.templates import (NonexistingSource, BaseTemplate, SimpleTemplate,
    MakoTemplate, Jinja2Template)
from swsg.sources import ReSTSource, MarkdownSource

SOURCE_NAME = u'temp-source.rest'
SOURCE_TEXT = u'some **important** text'
SIMPLE_TEMPLATE_TEXT = (u'''sources: temp-source.rest
<html><body><h1>{title}</h1><p>{content}</p></body></html>''')

FIRST_REAL_LINE = u'first real line of the template'
TEMPLATE_TEXT_MULTIPLE_SOURCES = (
    u'sources: foo.rest, bar.markdown\n' + FIRST_REAL_LINE)


def test_base_template_init():
    t = BaseTemplate(TEMPLATE_TEXT_MULTIPLE_SOURCES)
    source_names = list(t.source_names)
    assert source_names == [u'foo.rest', u'bar.markdown']
    assert t.text == FIRST_REAL_LINE
    t = BaseTemplate(FIRST_REAL_LINE)
    source_names = list(t.source_names)
    assert source_names == []
    assert t.text == FIRST_REAL_LINE


def test_base_template_get_sources(tmpdir):
    rest_text = u'text in the ReST file'
    foo = tmpdir.ensure('foo.rest')
    foo.check(file=True)
    foo.write(rest_text)
    markdown_text = u'text in the markdown file'
    bar = tmpdir.ensure('bar.markdown')
    bar.check(file=True)
    bar.write(markdown_text)
    t = BaseTemplate(TEMPLATE_TEXT_MULTIPLE_SOURCES)
    sources = t.get_sources(str(tmpdir))
    first_source, first_source_name = sources.next()
    assumed_source = ReSTSource(rest_text)
    assert first_source == assumed_source
    second_source, second_source_name = sources.next()
    assumed_source = MarkdownSource(markdown_text)
    assert second_source == assumed_source


def test_simple_template(tmpdir):
    template_text = SIMPLE_TEMPLATE_TEXT.format(
        title='$title', content='$content')
    template_file = tmpdir.ensure('template.html')
    template_file.check(file=True)
    template_file.write(template_text)

    source_filename = 'temp-source.rest'
    source_filename_path = tmpdir.ensure(source_filename)
    source_filename_path.check(file=True)
    source_filename_path.write(SOURCE_TEXT)

    template = SimpleTemplate(template_text)
    source_names = list(template.source_names)
    assert source_names == [source_filename]
    expected_result = (
        u'<html>'
          u'<body>'
            u'<h1>some **important** text</h1>'
            u'<p>'
              u'<p>some <strong>important</strong> text</p>\n'
            u'</p>'
          u'</body>'
        u'</html>')
    rendered_templates = template.render(str(tmpdir))
    source, output = rendered_templates.next()
    # make sure that there was rendered only one template
    py.test.raises(StopIteration, 'rendered_templates.next()')
    assert output == expected_result


def test_mako_template(tmpdir):
    mako = py.test.importorskip('mako')
    from mako import template
    # almost completely copied from mako's homepage
    template_text = u'''<%
    rows = [[v for v in range(0,10)] for row in range(0,10)]
%>
<table>
    % for row in rows:
        ${makerow(row)}
    % endfor
</table>
   
<%def name="makerow(row)">
    <tr>
    % for name in row:
        <td>${name}</td>
    % endfor
    </tr>
</%def>'''
    mako_template = template.Template(template_text)
    rendered_mako_template = mako_template.render()
    text = u'sources: {0}\n{1}'.format(SOURCE_NAME, template_text)
    swsg_mako_template = MakoTemplate(text)
    assert swsg_mako_template.text == template_text
    assert swsg_mako_template.source_names == [SOURCE_NAME]
    nonworking_template_generator = swsg_mako_template.render(str(tmpdir))
    # the source does not exist yet, so it cannot be rendered
    py.test.raises(NonexistingSource, 'nonworking_template_generator.next()')
    source_filename_path = tmpdir.ensure(SOURCE_NAME)
    source_filename_path.check(file=True)
    source_filename_path.write(SOURCE_TEXT)
    list_of_sources = list(swsg_mako_template.get_sources(str(tmpdir)))
    assert list_of_sources == [(ReSTSource(SOURCE_TEXT), SOURCE_NAME)]
    template_generator = swsg_mako_template.render(str(tmpdir))
    received_source_name, output = template_generator.next()
    assert received_source_name == SOURCE_NAME
    # make sure that there was rendered only one template
    py.test.raises(StopIteration, 'template_generator.next()')
    assert output == rendered_mako_template


def test_jinja2_template(tmpdir):
    jinja2 = py.test.importorskip('jinja2')
    template_text = u'''{% for item in range(10) -%}
        {{ item }}
    {%- endfor %}'''
    jinja_template = jinja2.Template(template_text)
    rendered_jinja_template = jinja_template.render()
    text = u'sources: {0}\n{1}'.format(SOURCE_NAME, template_text)
    swsg_jinja_template = Jinja2Template(text)
    assert swsg_jinja_template.text == template_text
    assert swsg_jinja_template.source_names == [SOURCE_NAME]
    nonworking_template_generator = swsg_jinja_template.render(str(tmpdir))
    # the source does not exist yet, so it cannot be rendered
    py.test.raises(NonexistingSource, 'nonworking_template_generator.next()')
    source_filename_path = tmpdir.ensure(SOURCE_NAME)
    source_filename_path.check(file=True)
    source_filename_path.write(SOURCE_TEXT)
    list_of_sources = list(swsg_jinja_template.get_sources(str(tmpdir)))
    assert list_of_sources == [(ReSTSource(SOURCE_TEXT), SOURCE_NAME)]
    template_generator = swsg_jinja_template.render(str(tmpdir))
    received_source_name, output = template_generator.next()
    assert received_source_name == SOURCE_NAME
    # make sure that there was rendered only one template
    py.test.raises(StopIteration, 'template_generator.next()')
    assert output == rendered_jinja_template


def test_genshi_template():
    py.test.importorskip('genshi')
    # FIXME: test me!
