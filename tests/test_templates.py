import py.test

from temp_utils import TemporaryProject

TEMPLATE_TEXT = u'''sources: temp-source.rest
<html><body><h1>{title}</h1><p>{content}</p></body></html>'''


def test_simple_template():
    project = TemporaryProject()
    with project as p:
        p.init()
        source = p.add_source(u'some **important** text')
        html_text = TEMPLATE_TEXT.format(title='$title', content='$content')
        expected_result = (
            u'<html>'
              u'<body>'
                u'<h1>temp-source</h1>'
                u'<p>'
                  u'<p>some <strong>important</strong> text</p>\n'
                u'</p>'
              u'</body>'
            u'</html>')
        template = p.add_template(html_text)
        for source, output in template.render():
            assert output == expected_result


def test_mako_template():
    py.test.importorskip('mako')


def test_jinja2_template():
    py.test.importorskip('jinja2')


def test_genshi_template():
    py.test.importorskip('genshi')
