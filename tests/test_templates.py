import py.test
from swsg.templates import BaseTemplate, SimpleTemplate
from swsg.sources import ReSTSource, MarkdownSource

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
    first_source = sources.next()
    assumed_source = ReSTSource(rest_text)
    assert first_source == assumed_source
    second_source = sources.next()
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
    # make sure that there was only one template rendered
    py.test.raises(StopIteration, 'rendered_templates.next()')
    assert output == expected_result


def test_mako_template():
    py.test.importorskip('mako')


def test_jinja2_template():
    py.test.importorskip('jinja2')


def test_genshi_template():
    py.test.importorskip('genshi')
