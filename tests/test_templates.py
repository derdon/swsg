import string
import os
import tempfile

import py.test
from swsg.templates import BaseTemplate, SimpleTemplate

SOURCE_FILENAME = u'temp-source.rest'
SOURCE_TEXT = u'some **important** text'
TEMPLATE_TEXT = string.Template(u'''sources: $temp_source
<html><body><h1>{title}</h1><p>{content}</p></body></html>''').safe_substitute(
    temp_source=SOURCE_FILENAME)


def test_base_template_init():
    first_real_line = u'first real line of the template'
    template_text = u'sources: foo.rest, bar.markdown\n' + first_real_line
    t = BaseTemplate(template_text)
    source_names = list(t.source_names)
    assert source_names == [u'foo.rest', u'bar.markdown']
    assert t.text == first_real_line
    t = BaseTemplate(first_real_line)
    source_names = list(t.source_names)
    assert source_names == []
    assert t.text == first_real_line


@py.test.mark.xfail
def test_simple_template(tmpdir):
    template_filename = tempfile.mkstemp()[1]
    html_text = TEMPLATE_TEXT.format(title='$title', content='$content')
    # write the template content into the temporary template file
    with open(template_filename, 'w') as fp:
        fp.write(html_text)
    # create the source directory manually
    tmpdir.ensure('sources', dir=True)
    source_dir = tmpdir.join('sources')
    # check if the source directory was created
    assert source_dir.check()
    # create a source file and fill it with content
    with open(str(tmpdir.join('sources', SOURCE_FILENAME)), 'w') as fp:
        fp.write(SOURCE_TEXT)
    template = SimpleTemplate(str(source_dir), template_filename)
    assert template.source_names == [SOURCE_FILENAME]
    expected_result = (
        u'<html>'
          u'<body>'
            u'<h1>temp-source</h1>'
            u'<p>'
              u'<p>some <strong>important</strong> text</p>\n'
            u'</p>'
          u'</body>'
        u'</html>')
    rendered_templates = template.render()
    source, output = rendered_templates.next()
    # make sure that there was only one template rendered
    py.test.raises(StopIteration, 'rendered_templates.next()')
    assert output == expected_result
    # remove the temporary template file
    os.remove(template_filename)


def test_mako_template():
    py.test.importorskip('mako')


def test_jinja2_template():
    py.test.importorskip('jinja2')


def test_genshi_template():
    py.test.importorskip('genshi')
